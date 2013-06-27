# -*- coding: utf-8 -*-
"""
Container 

"""
from base64 import b64encode
from oauth import oauth
import yaml
import urllib
import urllib2
import gzip
import cStringIO
import hashlib
import re
import os

from django.conf import settings
from django.template import loader
from django.utils.encoding import smart_str

from gsocial.utils.base import OAuthSignatureMethod_HMAC_SHA1_OPENSOCIAL, \
    get_session_data
from gsocial.log import Log
from gsocial.exceptions import ResponseError

from mobilejp.middleware.mobile import get_current_device


class Container(object):
    """
    Set the container in regard of Django`s settings.
    *container means "GreeAPI or MobageAPI"
    
    What this class do:
       Oauth authentication processing which uses the API.  
    
    Djangoの設定を判別してコンテナーをセットする
    ※コンテナーとは「GreeAPI, MobageAPIを指す」

    行なっていること
        Api周りのOauth認証処理

    """
    ResponseError = ResponseError

    # Get the last error cord.Needed at Blacklist.
    # 最終エラーコードを取得する。Blacklistで必要だった
    latest_error_code = None
    
    # Save the last response letters of oauth_request.
    # oauth_requestの最終レスポンス文字列を保存する
    latest_response = None

    def __init__(self, request=None):
        """
        Initialization.
        Setting container,etc.
        
        初期化

        containerのセットなど
        """
        self.container = get_containerdata()
        self.consumer_key = settings.CONSUMER_KEY
        self.consumer_secret = settings.CONSUMER_SECRET
        self.request = request
        self.token = None
        self.emoji_re = None  # encode_emoji、decode_emojiで使う
        self.emoji_decode_re = None  # decode_emojiで使う

    @property
    def name(self):
        """
        Retrun the name of container.
        
        containerの名前を返す
        """
        return self.container['container']

    @property
    def payment_success_status(self):
        """
        Return the "payment_success_status" of container.
        
        containerのpayment_success_statusを返す
        """
        return self.container['payment_success_status']

    @property
    def payment_cancel_status(self):
        """
        Return the "payment_cancel_status" of container.
        
        containerのpayment_cancel_statusを返す
        """
        return self.container['payment_cancel_status']

    def payment_template(self):
        """
        Return the payment template.
        paymentのテンプレートを返す
        """
        return loader.get_template('opensocial/payment/'+ self.container['payment_info_template'])

    @property
    def monthly_payment_template(self):
        """
        Return the monthly_payment template.
        monthly_paymentのテンプレートを返す
        """
        return loader.get_template('opensocial/monthly_payment/'+ self.container['payment_info_template'])

    def get_token(self):
        """
        Return the oauth_token.
        oauth_tokenを返す

        """
        if self.token:
            return self.token

        oauth_token = oauth_token_secret = None
        if self.request:
            if get_current_device().is_smartphone:
                #For smart phone
                # スマートフォン用
                session_data = get_session_data(self.request)
                oauth_token = session_data['oauth_token']
                oauth_token_secret = session_data['oauth_token_secret']
            else:
                #For feature phone
                # フィーチャーフォン用
                auth_string = self.request.META.get('HTTP_AUTHORIZATION','')
                if auth_string:
                    for param in auth_string.split(','):
                        keyValuePair = param.strip().split('=', 1)
                        if len(keyValuePair) == 2:
                            value = keyValuePair[1].strip('"').encode('utf-8')
                            if keyValuePair[0] == 'oauth_token':
                                oauth_token = value
                            if keyValuePair[0] == 'oauth_token_secret':
                                oauth_token_secret = value

        if oauth_token_secret and oauth_token:
            self.token = oauth.OAuthToken(oauth_token, oauth_token_secret)

        return self.token


    def _create_endpoint_url(self, path, secure=False, url_tail=None):
        """
        FP/SP/WEBVIEW判定し対応したendpoint_urlを返す
        """

        protocol = 'https' if secure else 'http'

        from mobilejp.middleware.mobile import get_current_device
        device = get_current_device()

        if device:
            if device.is_webview:
                endpoint = self.container['endpoint_webview']
            elif device.is_smartphone:
                endpoint = self.container['endpoint_sp']
            else:
                endpoint = self.container['endpoint_fp']
        else:
            endpoint = self.container['endpoint_fp']

        Log.debug("url_tail %s " % url_tail)


        if url_tail or url_tail == '':
            url = '%s://%s%s%s' % (protocol, endpoint, url_tail, path)
        else:
            url = '%s://%s%s%s' % (protocol, endpoint, self.container['api_url_tail'], path)

        return url

    def oauth_request(self, method, requestor_id, path, data=None, headers=None, params=None, url_tail=None, secure=False, body_hash=False):
        """
        Do Oauth request.
        
        Arguments:
         method: HTTP_METHOD
         requestor_id: opensocial_owner_id
         path: access_path
            exp:
                pyament:'/api/rest/payment/@me/@self/@app'
                inspection: '/api/rest/inspection/@app'
         data: default:None
         headers: default:None
            exp:
                payment:{'Content-Type': 'application/json; charset=utf8'}
         params: default:None
         url_tail: default:None
         secure: Use Http or not？ default:False
         body_hash: default:False
         
        Return value:
         OAuthRequestresponse body
        
        OAuthリクエストを行う

        引数
         method: HTTP_METHOD
         requestor_id: opensocial_owner_id
         path: access_path
            exp:
                pyament:'/api/rest/payment/@me/@self/@app'
                inspection: '/api/rest/inspection/@app'
         data: default:None
         headers: default:None
            exp:
                payment:{'Content-Type': 'application/json; charset=utf8'}
         params: default:None
         url_tail: default:None
         secure: Httpsにするか？ default:False
         body_hash: default:False

        返り値
         OAuthRequestresponse body

        """
        self.latest_error_code = None
        self.latest_response = None

        headers = headers or {}
        #Log.debug('method', method)
        #Log.debug('consumer_key', self.consumer_key)
        #Log.debug('consumer_secret', self.consumer_secret)

        consumer = oauth.OAuthConsumer(self.consumer_key, self.consumer_secret)
        signature_method_hmac_sha1 = OAuthSignatureMethod_HMAC_SHA1_OPENSOCIAL()

        #endpoint url 生成 
        url = self._create_endpoint_url(path, secure, url_tail)

        Log.debug("url:", url)

        os_params = params or {}
        os_params['xoauth_requestor_id'] = requestor_id

        if data:
            data = smart_str(data, 'utf-8')
        
        #いらないのでコメントアウト
        if body_hash:
            os_params['oauth_body_hash'] = b64encode(hashlib.sha1(data).digest())

        Log.debug('url', url)
        Log.debug('os_params', os_params)

        # access protected resources
        oauth_request = oauth.OAuthRequest.from_consumer_and_token( consumer,
                                                                    token=self.get_token(),
                                                                    http_method=method,
                                                                    http_url=url,
                                                                    parameters=os_params )
        oauth_request.sign_request(signature_method_hmac_sha1, consumer, self.get_token())
        os_headers = oauth_request.to_header()
        Log.debug('os_headers', os_headers)

        if os_headers:
            headers.update(os_headers)
        if os_params:
            url = '%s?%s' % (url, urllib.urlencode(os_params))

        #try:
        req = urllib2.Request(url, data, headers)
        req.add_header('Accept-encoding', 'gzip')
        if method not in ('GET', 'POST'):
            req.get_method = lambda : method
        Log.debug('method', method)
        Log.debug('url', url)
        Log.debug('data', data)
        Log.debug('headers', headers)

        res = None
        #    try:
        Log.debug('start', "")
        ins = urllib2.urlopen(req)
        Log.debug('ins', ins)
        res = ins.read()
        Log.debug('res', res)
        if ins.headers.get('content-encoding', None) == 'gzip':
            res = gzip.GzipFile(fileobj=cStringIO.StringIO(res)).read()
        ##    except urllib2.HTTPError, e:
        #        #Some Python version might raise error when 201/202 has returned.
        #        # Pythonで201/202だと例外を送出しちゃうバージョンあり
        #        Log.debug('HTTPError code:%d' % (e.code, ), e)

        #        self.latest_error_code = e.code
        #        if not (e.code == 201 or e.code ==202): 
        #            if not settings.OPENSOCIAL_DEBUG:
        #                raise e
        #            else:
        #                print e
        #        if res is None:
        #            res = e.read()
        #        else:
        #            Log.debug('res is not None.', res)
        #except:
        #    import sys
        #    Log.debug('sys.exc_info()', sys.exc_info())
        #    import traceback
        #    Log.debug('traceback.print_exc()', traceback.print_exc())
        #    res = None

        Log.debug('response', res)
        self.latest_response = res
        return res

    def encode_emoji(self, text):
        """
        Encode "Emoji" and return it.
        For Gree`s InspectionAPI 
        eg.  \ue000 -> &#xe000 
        
        argument:
         text
        return value:
         encoded "emoji" 
         
        絵文字をエンコードして返す
        GREEのInspectionAPI、モバゲーのTextDataAPI用
        \ue000 -> &#xe000 に変換

        引数
         text

        返り値
         エンコードした絵文字を返す
        """
        Log.debug('encode_emoji before: %r' % text)

        if self.emoji_re is None:
            self.emoji_re = re.compile(u'[\ue000-\uf0fc]')

        def emoji_open(m):
            return '&#x%x' % ord(m.group(0))

        encoded = self.emoji_re.sub(emoji_open, text)
        Log.debug('encode_emoji after: %r' % encoded)
        return encoded

    def decode_emoji(self, text):
        """
        Decode "Emoji" and return it.
        For Gree`s InspectionAPI 
        eg. &#xe000 -> \ue000
        if &#xXXXX is not "Emoji" it will become null.
        
        argument:
         text
        return value:
         decoded "emoji"  
         
        絵文字をデコードして返す
        GREEのInspectionAPI、モバゲーのTextDataAPI用
        &#xe000 -> \ue000に変換
        絵文字じゃない &#xXXXX は空文字にする

        引数
         text

        返り値
         デコードした絵文字を返す
        """
        Log.debug('decode_emoji before: %r' % text)

        if self.emoji_re is None:
            self.emoji_re = re.compile(u'[\ue000-\uf0fc]')
        if self.emoji_decode_re is None:
            self.emoji_decode_re = re.compile(r'&#x(\w{4})')

        def emoji_close(m):
            c = unichr(int(m.group(1), 16))
            if self.emoji_re.search(c):
                return c
            else:
                return ''

        decoded = self.emoji_decode_re.sub(emoji_close, text)
        Log.debug('decode_emoji after: %r' % decoded)
        return decoded


#file_path = '/Users/yamada_yoshiyuki/gumi_works/genju-hime/application/submodule/opensocial/container_list.yaml'
#file_path = 'submodule/opensocial/container_list.yaml'
file_path = os.path.dirname(os.path.abspath(__file__)) + '/container_list.yaml'
CONTAINERS = yaml.load(open(file_path).read())


def get_containerdata():
    """
    Return the data of container specified by the settings.
    
    settingsの指定されたcontainerのデータを返す
    """
    os_container = settings.OPENSOCIAL_CONTAINER
#    if settings.IS_WEBVIEW:
#        os_container += '_net'
    container = CONTAINERS[os_container]
    container['spacer_url'] = container['spacer_url'] % ({'spacer_url':settings.MEDIA_URL})
    Log.debug("container_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    Log.debug("container os_container: %s" % os_container)
    Log.debug("container endpoint: %s" % container['endpoint'])
    Log.debug("container_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    return container

def get_containername():
    """
    Return the container name
    gree or mixi or mbga
    
    container名を返す
    mixi or mbga or gree
    """
    return get_containerdata()['container']


containerdata = get_containerdata()
containername = get_containername()
