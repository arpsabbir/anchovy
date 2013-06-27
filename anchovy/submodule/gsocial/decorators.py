# -*- coding: utf-8 -*-
"""
gsocial decorator
"""
import threading
import re
import hmac
import base64
import hashlib
import urllib
from gsocial.log import Log
import binascii
from Crypto.PublicKey import RSA
from oauth.oauth import OAuthRequest as Request
from oauth.oauth import OAuthError as Error
from oauth import oauth
from oauth.oauth import escape, _utf8_str

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from gsocial.http import HttpResponseNotAuthorized
from gsocial.models import get_osuser
from gsocial.set_container import containerdata, user_attr
from gsocial.setting import GREE, GREE_NET


OAUTH2_ENABLE = False
THREAD_LOCAL = None

def set_thread_local_session_id(session_id):
    """
    セッションIDをスレッドローカルにセットする
    """
    global THREAD_LOCAL
    if THREAD_LOCAL is None:
        THREAD_LOCAL = threading.local()
    THREAD_LOCAL.session_id = session_id

def get_thread_local_session_id():
    """
    セッションIDをスレッドローカルを取得
    """
    global THREAD_LOCAL
    if THREAD_LOCAL:
        return THREAD_LOCAL.session_id

    return None


class Request2(Request):
    """
    get_normalized_parameters において、
    同名のキー（POSTにおけるhoge_id=1&hoge_id=2)
    が1つにまとめられ、 Authに失敗するため処置する
    """
    def get_normalized_parameters(self):
        """Return a string that contains the parameters that must be signed."""
        params = self.parameters
        try:
            # Exclude the signature if it exists.
            del params['oauth_signature']
        except:
            pass
        # Escape key values before sorting.
        key_values = []
        for key, value in params.iteritems():
            if isinstance(value, basestring):
                esc_value = escape(_utf8_str(value))
                esc_key = escape(_utf8_str(key))
                key_values.append((esc_key, esc_value))
            else:
                try:
                    esc_value = escape(_utf8_str(value))
                    esc_key = escape(_utf8_str(key))
                    list(value)
                except TypeError, error:
                    assert 'is not iterable' in str(error)
                    key_values.append((esc_key, esc_value))
                else:
                    key_values.extend((escape(_utf8_str(key)), escape(_utf8_str(item)) if isinstance(item, basestring) else item) for item in value)

        # Sort lexicographically, first after key, then after value.
        key_values.sort()
        # Combine key value pairs into a string.
        return '&'.join(['%s=%s' % (key, value) for key, value in key_values])

def create_message(request, params):
    """
    create_message
    """
    host = request.get_host()
    host = host.split(',')[0]
    http_head = request.is_secure() and 'https://' or 'http://'
    base_url = http_head + host + request.path
    OutputLog.debug('base_url: %s' % base_url)
    oauth_request = Request2(
        request.method,
        base_url, 
        params)

    message = '&'.join((
            oauth.escape(oauth_request.get_normalized_http_method()),
            oauth.escape(oauth_request.get_normalized_http_url()),
            oauth.escape(oauth_request.get_normalized_parameters()),
            ))

    OutputLog.debug("message: %s" %  message)

    return message

def create_rsa_hash(request, params):
    """
    rsa_hash生成
    """
    message = create_message(request, params)
    return hashlib.sha1(message).digest()

def create_hmac_hash(request, params, oauth_token_secret):
    """
    hmac_hash生成
    """
    message = create_message(request, params)
    shared_key = '%s&%s' % (oauth.escape(settings.CONSUMER_SECRET), 
                            oauth.escape(oauth_token_secret))
    OutputLog.debug('shared_key: %s' % shared_key)
    hashed = hmac.new(shared_key, message, hashlib.sha1)
    return hashed.digest()

def signed_request(view_func):
    """
    sighened_requestデコレーター
    """
    def _verify_sign(request, *args, **kw):
        request.opensocial_container = containerdata

        header_params = {}
        oauth_signature = request.REQUEST.get("oauth_signature", None)
        if oauth_signature == None:
            auth_string = request.META.get('HTTP_AUTHORIZATION', "")
            auth_string = auth_string.replace('OAuth ', "")
            OutputLog.debug('HTTP_AUTHORIZATION: %s' % auth_string)
            if auth_string:
                for param in auth_string.split(','):
                    OutputLog.debug(param)
                    (key, value) = param.strip().split('=', 1)
                    value = value.strip('"').encode('utf-8')
                    if key == 'oauth_signature':
                        oauth_signature = value
                    elif key != 'OAuth realm' and key != 'realm':
                        header_params[key] = value

        if oauth_signature == None:
            OutputLog.error('oauth signature not found')
            return HttpResponseNotAuthorized(request.get_full_path())

        sig = base64.decodestring(
            urllib.unquote(oauth_signature))

        # Construct a RSA.pubkey object
        exponent = long(65537)
        public_key_long = long(containerdata['hex_cert'], 16)
        public_key = RSA.construct((public_key_long, exponent))
        # create remote hash
        remote_hash = public_key.encrypt(sig, '')[0][-20:]

        try:
            # コンテナによって、base_stringを作成するのにクエリパラメータのみを使うもの、
            # postdataも含めるものがあるので、両方のパターンのハッシュを作り
            # どちらかがマッチすれば認証OKとする。

            get_params = {}
            for key, value in request.GET.items():
                if key != 'oauth_signature':
                    get_params[key] = value.encode('utf-8')
            OutputLog.debug(get_params)

            post_params = {}
            for key, value in request.POST.items():
                if key != 'oauth_signature':
                    post_params[key] = value.encode('utf-8')
            OutputLog.debug(post_params)

            # Authorithationヘッダのみを使って作ったハッシュ
            local_hash1 = create_rsa_hash(request, header_params)

            # GETパラメータのみを使ってハッシュを作成
            local_hash2 = create_rsa_hash(request, get_params)

            # Authorithationヘッダ + GETパラメータ
            header_params.update(get_params)
            local_hash3 = create_rsa_hash(request, header_params)

            # GETパラメータ + POSTパラメータ
            get_params.update(post_params)
            local_hash4 = create_rsa_hash(request, get_params)

            # Authorithationヘッダ + GETパラメータ + POSTパラメータ
            header_params.update(post_params)
            local_hash5 = create_rsa_hash(request, header_params)

            # Verify that the locally-built value matches the value
            # from the remote server
            #OutputLog.debug("remote_hash: %s" %  remote_hash)
            OutputLog.debug(
                "local_hash: 1:A:%s, 2:G:%s, 3:A+G:%s, 4:G+P:%s, 5:A+G+P:%s" % (
                (local_hash1 == remote_hash),
                (local_hash2 == remote_hash),
                (local_hash3 == remote_hash),
                (local_hash4 == remote_hash),
                (local_hash5 == remote_hash)
            ))
            if local_hash1 != remote_hash and \
               local_hash2 != remote_hash and \
               local_hash3 != remote_hash and \
               local_hash4 != remote_hash and \
               local_hash5 != remote_hash:
                raise

        except Error, err:
            OutputLog.error('oauth error: %s' % err.message)
            return HttpResponseNotAuthorized(request.get_full_path())
        except:
            import sys
            exception_type, exception_value, exception_traceback = sys.exc_info()
            OutputLog.error('Invalid OAuth Signature.: %s %s' % (exception_type, exception_value))
            OutputLog.error('HTTP_AUTHORIZATION: %s' % auth_string)
            OutputLog.error("remote_hash: %r" %  remote_hash)
            OutputLog.error("local_hash1 A: %r %r" %  (local_hash1, (local_hash1 == remote_hash)))
            OutputLog.error("local_hash2 G: %r %r" %  (local_hash2, (local_hash2 == remote_hash)))
            OutputLog.error("local_hash3 A + G: %r %r" %  (local_hash3, (local_hash3 == remote_hash)))
            OutputLog.error("local_hash4 G + P: %r %r" %  (local_hash4, (local_hash4 == remote_hash)))
            OutputLog.error("local_hash5 A + G + P: %r %r" %  (local_hash5, (local_hash5 == remote_hash)))
            return HttpResponseNotAuthorized(request.get_full_path())
        else:
            request.opensocial_userid = str(request.REQUEST['opensocial_viewer_id'])
            return view_func(request, *args, **kw)
        _verify_sign.__doc__ = view_func.__doc__
        _verify_sign.__dict__ = view_func.__dict__
    return _verify_sign


def create_hashed_debug_user_id(request):
    """
    requestから、ランダムなユーザーIDを作成する。
    HTTP_USER_AGENT と、REMOTE_ADDR から一意なIDを生成。
    ※デコレータでは無い。oauth_signature_required から呼ばれる。
    """

    bulk_user_id = request.META.get('HTTP_USER_AGENT')
    hashed_debug_osuser_number = int(hashlib.sha1(bulk_user_id).hexdigest()[5:11], 16)
    hashed_debug_osuser_number = hashed_debug_osuser_number % 100000000
    opensocial_debug_user_id = hashed_debug_osuser_number  + 9900000000
    return str(opensocial_debug_user_id)

def oauth_signature_required(view_func):
    """
    oauth_signature_required
    """

    def _verify_sign(request, *args, **kw):
        """
        _verify_sign
        """
        from mobilejp.middleware.mobile import get_current_device
        device = get_current_device();

#        # デバッグユーザーの（空）認証
#        if settings.OPENSOCIAL_DEBUG:
#            if settings.OPENSOCIAL_DEBUG_USER_ID:
#                opensocial_owner_id = settings.OPENSOCIAL_DEBUG_USER_ID
#            else:
#                opensocial_owner_id = create_hashed_debug_user_id(request)
#            request.opensocial_userid = opensocial_owner_id
#            request.session_id = 'test%s' % opensocial_owner_id
#            return view_func(request, *args, **kw)

        request.is_smartphone = False
        request.is_futurephone = False
        from mobilejp.middleware.mobile import get_current_device
        device = get_current_device();
        if device and device.is_nonmobile() and\
           not request.path.startswith('/m/appevent/'):
            # PCユーザーの認証
            request.is_smartphone = True
            if settings.OPENSOCIAL_DEBUG or settings.OPENSOCIAL_SANDBOX:
                settings.TEMPLATE_DIRS = settings.SMARTPHONE_TEMPLATE_DIRS
            out = _verify_sign_pc(request, *args, **kw)

            return out
        elif settings.OPENSOCIAL_SMARTPHONE_DEBUG:
            # ローカルスマフォ対応でのテスト用
            request.is_smartphone = True
            if settings.OPENSOCIAL_DEBUG or settings.OPENSOCIAL_SANDBOX:
                settings.TEMPLATE_DIRS = settings.SMARTPHONE_TEMPLATE_DIRS
            out = _verify_sign_pc(request, *args, **kw)

            return out
        else:
            # 携帯ユーザーの認証
            request.is_futurephone = True
            if settings.OPENSOCIAL_DEBUG or settings.OPENSOCIAL_SANDBOX:
                settings.TEMPLATE_DIRS = settings.FUTUREPHONE_TEMPLATE_DIRS
            out = _verify_sign_mobile(request, *args, **kw)
            return out


    def _verify_sign_pc(request, *args, **kw):
        """
        pc用
        """

        # セッションIDはCOOKIESからもREQUESTからも取得しようとする。
        # Safariの制限で初ページはCOOKIESを使えない
        # クッキーからセッションID取得
        session_id_from_request = False
        session_id = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        if not session_id:
            # リクエストパラメータからセッションID取得
            session_id_from_request = True
            session_id = request.REQUEST.get(settings.SESSION_URL_KEY_NAME, None)

        OutputLog.debug('REQUEST REQUEST %s' % request.REQUEST)
        OutputLog.debug('REQUEST COOKIES %s' % request.COOKIES)
        OutputLog.debug('REQUEST META %s' % request.META)
        OutputLog.debug('_verify_sign_pc:session_id %s' % session_id)

        # 有効セッションIDの場合、view_funcを呼び出して終わる       
        if session_id is not None:
            if session_id_from_request and request.path == '/m/':
                # トップページ表示かつセッションIDがリクエストパラメータ経由できた場合、認証成功画面を表示
                res = render_to_response(settings.SMARTPHONE_AUTH_SUCCESS_TEMPLATE,
                      RequestContext(request, {'scid':session_id}))
                res.set_cookie(settings.SESSION_COOKIE_NAME, session_id)
                return res

            engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
            request.session = engine.SessionStore(session_id)
            #session_data = tt_operator.getobj(session_id);
            if 'opensocial_userid' in request.session:

                request_userid = request.REQUEST.get("opensocial_viewer_id", None)

                if request.session.get_expiry_age() <= 0:

                    # セッションIDで認証できない
                    request.session.flush()
                    OutputLog.warn('*** delete expire_time ****')
                elif request_userid and str(request_userid) != request.session['opensocial_userid']:

                    #　セッションIDで認証できない（同じiPhoneから別アカウント）
                    request.session.flush()
                    OutputLog.warn('*** delete different user ****')
                else:

                    # 認証成功！certificateチェックが要らない！
                    request.session.set_expiry(60 * 30) 

                    request.opensocial_userid = request.session['opensocial_userid']
                    request.session_id = request.session.session_key

                    OutputLog.debug('_verify_sign_pc:already session_data %s' % request.session)
                    return view_func(request, *args, **kw)

        # certificateチェックが必要です。
#        session_id = str(uuid.uuid4())
#        request.session_id = session_id
        request.session['session_data'] = True
        request.session_id = request.session.session_key

        if settings.OPENSOCIAL_DEBUG:
            if settings.OPENSOCIAL_DEBUG_USER_ID:
                opensocial_owner_id = settings.OPENSOCIAL_DEBUG_USER_ID
            else:
                opensocial_owner_id = create_hashed_debug_user_id(request)
            request.opensocial_userid = opensocial_owner_id
            request.session['opensocial_userid'] = opensocial_owner_id
            request.session['oauth_token'] = None
            request.session['oauth_token_secret'] = None
            request.session.set_expiry(60 * 30)

            request.session_id = request.session.session_key
            request.session.save()

            OutputLog.debug('_verify_sign_pc:session oauth_token %s' % request.session['oauth_token'])
            OutputLog.debug('_verify_sign_pc:session oauth_token_secret %s' %
                            request.session['oauth_token_secret'])
            OutputLog.debug('_verify_sign_pc:session_id %s' % request.session_id)
            #set_thread_local_session_id(request.session_id)
            return view_func(request, *args, **kw)

        user_agent = request.META.get('HTTP_USER_AGENT', "")
        if not device.is_smartphone:
            OutputLog.error('UA error : %s' % user_agent)
            ctxt = RequestContext(request, {
                "message": "ﾕｰｻﾞｰ認証が失敗しました。もう一度ﾛｸﾞｲﾝしてください。",
            })
            return render_to_response(settings.SMARTPHONE_ERROR_BLOCK_TEMPLATE, ctxt)

        try:
            auth_string = request.META.get('QUERY_STRING', "")
            OutputLog.debug('QUERY_STRING: %s' % auth_string)
            if not auth_string:
                OutputLog.debug('check step 1')
                raise
            params = {}
            remote_hash = None
            for param in auth_string.split('&'):
                OutputLog.debug(param)
                (key, value) = param.strip().split('=', 1)
                value = value.strip('"').encode('utf-8')

                if key == 'oauth_signature':
                    remote_hash = base64.decodestring(urllib.unquote(value))
                elif key and key != 'OAuth realm':
                    params[key] = value

            OutputLog.debug('auth step 1')
            OutputLog.debug(params)

            if not remote_hash:
                OutputLog.debug('check step 2')
                raise

            oauth_token_secret = params.get('oauth_token_secret', '')

            # コンテナによって、base_stringを作成するのにクエリパラメータのみを使うもの、
            # postdataも含めるものがあるので、両方のパターンのハッシュを作り
            # どちらかがマッチすれば認証OKとする。
            encoding = request.encoding
            if not encoding:
                encoding = 'utf-8'

            for key, value in request.GET.items():
                if key and key != 'oauth_signature':
                    params[key] = value.encode(encoding)

            OutputLog.debug('auth step 2')
            OutputLog.debug(params)

            # クエリパラメータのみを使ってハッシュを作成
            local_hash1 = create_hmac_hash(request, params, oauth_token_secret)

            # POSTDATAも含めたパラメータを使ってハッシュを作成
            for key, value in request.POST.items():
                if key and key != 'oauth_signature':
                    params[key] = value.encode(encoding)

            OutputLog.debug('auth step 3')
            OutputLog.debug(params)

            local_hash2 = create_hmac_hash(request, params, oauth_token_secret)

            # Verify that the locally-built value matches the value
            # from the remote server
            OutputLog.debug("remote_hash: %s" %  remote_hash)
            OutputLog.debug("local_hash1 G: %s %s" %  (local_hash1, (local_hash1 == remote_hash)))
            OutputLog.debug("local_hash2 G + P: %s %s" %  (local_hash2, (local_hash2 == remote_hash)))
            OutputLog.debug("local_hash1 result: %s" %  (local_hash1 == remote_hash))
            OutputLog.debug("local_hash2 result: %s" %  (local_hash2 == remote_hash))
            if local_hash1 != remote_hash and local_hash2 != remote_hash:
                OutputLog.debug('check step 3')
                raise
        except oauth.OAuthError, err:
            request.session.flush()
            OutputLog.error('oauth error: %s' % err.message)
            #return HttpResponseNotAuthorized(request.get_full_path()), False
            ctxt = RequestContext(request, {
                "message": "ﾕｰｻﾞｰ認証が失敗しました。もう一度ﾛｸﾞｲﾝしてください。",
            })
            return render_to_response(settings.SMARTPHONE_ERROR_TEMPLATE, ctxt)
        except:
            import sys
            request.session.flush()
            exception_type, exception_value, exception_traceback = sys.exc_info()
            OutputLog.error('Invalid OAuth Signature.: %s %s' % (exception_type, exception_value))
            #return HttpResponseNotAuthorized(request.get_full_path()), False

            ctxt = RequestContext(request, {
                "message": "ﾕｰｻﾞｰ認証が失敗しました。もう一度ﾛｸﾞｲﾝしてください。",
            })
            return render_to_response(settings.SMARTPHONE_ERROR_TEMPLATE, ctxt)
        else:
            request.opensocial_userid = str(request.GET["opensocial_viewer_id"])
            #request.session_id = session_id
            OutputLog.debug('Request Set')

            OutputLog.debug('_check_certificate:success request %s' % request.REQUEST)
            if settings.OPENSOCIAL_DEBUG:
                if settings.OPENSOCIAL_DEBUG_USER_ID:
                    opensocial_owner_id = settings.OPENSOCIAL_DEBUG_USER_ID
                else:
                    opensocial_owner_id = create_hashed_debug_user_id(request)
                request.opensocial_userid = opensocial_owner_id
                request.session['opensocial_userid'] = opensocial_owner_id
                request.session['oauth_token'] = None
                request.session['oauth_token_secret'] = None
                request.session.set_expiry(60 * 30)
#                session_data = {
#                                'opensocial_userid' : opensocial_owner_id, 
#                                'expire_time' : time.time() + 60*30,
#                                'oauth_token' : None,
#                                'oauth_token_secret' : None,
#                                }
            else:
#                session_data = {
#                                'opensocial_userid' : request.REQUEST['opensocial_viewer_id'], 
#                                'expire_time' : time.time() + 60*30,
#                                'oauth_token' : request.REQUEST['oauth_token'],
#                                'oauth_token_secret' : request.REQUEST['oauth_token_secret'],
#                                }
                request.session['opensocial_userid'] = request.REQUEST['opensocial_viewer_id']
                request.session['oauth_token'] = request.REQUEST['oauth_token']
                request.session['oauth_token_secret'] = request.REQUEST['oauth_token_secret']
                request.session.set_expiry(60 * 30)
                
                # WebViewアプリ情報をapp_user_agentに設定
                request.session['app_user_agent'] = device.name
                if device.is_webview:
                    request.session['is_webview'] = True
                    user_attr.container = GREE_NET                                                                 
                    if settings.OPENSOCIAL_DEBUG or settings.OPENSOCIAL_SANDBOX:                                   
                        user_attr.container = 'sb.%s' % GREE_NET
                        Log.debug('container: %s' % user_attr.container)

            #tt_operator.setobj(session_id, session_data)
            #response.set_cookie("session_id", session_id)
            request.session_id = request.session.session_key
            request.session.save()

            OutputLog.debug('_verify_sign_pc:session oauth_token %s' % request.session['oauth_token'])
            OutputLog.debug('_verify_sign_pc:session oauth_token_secret %s' % request.session['oauth_token_secret'])
            OutputLog.debug('_verify_sign_pc:session_id %s' % request.session_id)
            # 認証成功画面を表示
            res = render_to_response(settings.SMARTPHONE_AUTH_SUCCESS_TEMPLATE,
                RequestContext(request, {'scid':request.session_id}))
            res.set_cookie(settings.SESSION_COOKIE_NAME, request.session_id)
            return res
        _verify_sign.__doc__ = view_func.__doc__
        _verify_sign.__dict__ = view_func.__dict__

        return response



    def _verify_sign_mobile(request, *args, **kw):
        """
        モバイル版
        """
        request.opensocial_container = containerdata
        if settings.IS_STRESS_TEST:
            opensocial_owner_id = request.REQUEST.get('opensocial_owner_id', None)
            if opensocial_owner_id is None:
                opensocial_owner_id = create_hashed_debug_user_id(request)
                request.opensocial_userid = str(opensocial_owner_id)
                return view_func(request, *args, **kw)

        if settings.OPENSOCIAL_DEBUG:
            if settings.OPENSOCIAL_DEBUG_USER_ID:
                opensocial_owner_id = settings.OPENSOCIAL_DEBUG_USER_ID
            else:
                #OPENSOCIAL_DEBUG_USER_ID = False とか、 "" だった場合、ユーザーエージェントとIPアドレスからユーザーIDを生成
                opensocial_owner_id = create_hashed_debug_user_id(request)
            request.opensocial_userid = str(opensocial_owner_id)
            return view_func(request, *args, **kw)

        try:
            auth_string = request.META.get('HTTP_AUTHORIZATION', "")
            auth_string = auth_string.replace('OAuth ', "")
            OutputLog.debug('HTTP_AUTHORIZATION: %s' % auth_string)
            params = {}
            for param in auth_string.split(','):
                OutputLog.debug(param)
                (key, value) = param.strip().split('=', 1)
                value = value.strip('"').encode('utf-8')
                if key == 'oauth_signature':
                    remote_hash = base64.decodestring(urllib.unquote(value))
                elif key and key != 'OAuth realm' and key != 'realm':
                    params[key] = value
            OutputLog.debug(params)
            if not remote_hash:
                raise

            oauth_token_secret = params.get('oauth_token_secret', '')

            # コンテナによって、base_stringを作成するのにクエリパラメータのみを使うもの、
            # postdataも含めるものがあるので、両方のパターンのハッシュを作り
            # どちらかがマッチすれば認証OKとする。
            encoding = request.encoding
            if not encoding:
                encoding = 'utf-8'

            for key, value in request.GET.items():
                if key and key != 'oauth_signature':
                    params[key] = value.encode(encoding)
            OutputLog.debug(params)

            local_hash1 = local_hash2 = u''

            # クエリパラメータのみを使ってハッシュを作成
            local_hash1 = create_hmac_hash(request, params, oauth_token_secret)

            # POSTDATAも含めたパラメータを使ってハッシュを作成
            for key, value in request.POST.lists():
                if len(value) == 1:
                    value = ','.join(value)
                    if key and key != 'oauth_signature':
                        params[key] = value.encode(encoding)
                else:
                    # リストである場合
                    for i, v in enumerate(value):
                        try:
                            value[i] = int(v)
                        except TypeError:
                            value[i] = v.encode(encoding)
                    params[key] = value

            local_hash2 = create_hmac_hash(request, params, oauth_token_secret)

            host = request.get_host()
            host = host.split(',')[0]
            base_url = request.is_secure() and 'https://' or 'http://' + host + request.path

            OutputLog.info("base_url: %s" % (base_url))
            for key, value in params.iteritems():
                if isinstance(value, basestring):
                    OutputLog.info("%s: %s" % (key, value.decode(encoding)))
                else:
                    OutputLog.info("%s: %s" % (key, value))
            OutputLog.info("raw: %s" % request.raw_post_data)
            #OutputLog.info("hash_test: %s" % hash_test)
            OutputLog.info("remote_hash: %s" % binascii.b2a_base64(remote_hash)[:-1])
            OutputLog.info("local_hash1: %s" % binascii.b2a_base64(local_hash1)[:-1])
            OutputLog.info("local_hash2: %s" % binascii.b2a_base64(local_hash2)[:-1])

            OutputLog.info("local_hash: 1:A:%s, 2:G+P:%s" % (
                (local_hash1 == remote_hash),
                (local_hash2 == remote_hash)
            ))

            # Verify that the locally-built value matches the value
            # from the remote server
            #OutputLog.debug("remote_hash: %s" %  remote_hash)
            OutputLog.debug("local_hash: 1:A:%s, 2:G+P:%s" % (
                (local_hash1 == remote_hash),
                (local_hash2 == remote_hash)
            ))

            if local_hash1 != remote_hash and local_hash2 != remote_hash:
                raise
        except Error, err:
            OutputLog.error('oauth error: %s' % err.message)
            return HttpResponseNotAuthorized(request.get_full_path())
        except:
            import sys
            exception_type, exception_value, exception_traceback = sys.exc_info()
            OutputLog.error('Invalid OAuth Signature.: %s %s' % (exception_type, exception_value))
            OutputLog.error('HTTP_AUTHORIZATION: %s' % auth_string)
            #OutputLog.debug("local_hash: 1:A:%s, 2:G+P:%s" % (
            #    (local_hash1 == remote_hash),
            #    (local_hash2 == remote_hash)
            #))

            return HttpResponseNotAuthorized(request.get_full_path())
        else:
            opensocial_owner_id = request.REQUEST.get('opensocial_owner_id', None)
            if opensocial_owner_id is not None:
                request.opensocial_userid = str(opensocial_owner_id)
            return view_func(request, *args, **kw)
        _verify_sign.__doc__ = view_func.__doc__
        _verify_sign.__dict__ = view_func.__dict__


    return _verify_sign

def require_osuser(view_func):
    def decorate(request, *args, **kwds):

        """
        require_osuser
        """
        from django.core.urlresolvers import reverse
        from submodule.gsocial.http import HttpResponseOpensocialRedirect
        if settings.DEBUG and settings.OPENSOCIAL_SANDBOX and settings.IS_LOCAL_AUTH:
            if not request.user.is_authenticated():
                return HttpResponseOpensocialRedirect(reverse('mobile_auth_login'), request)

        assert hasattr(request, 'opensocial_userid'), "require_osuser requires singned_request or oauth_signature_required decolator."

        # ゲームができるユーザーの制限追加
        from gsocial.utils.restrictive.api import get_restrictive_api
        restrictive_api = get_restrictive_api(request.opensocial_userid)
#        return HttpResponseOpensocialRedirect(reverse('mobile_not_playable'), request)
        if not restrictive_api.can_playable():
            return HttpResponseOpensocialRedirect(reverse('mobile_not_playable'), request)

        # OpenSocialUserを取得する
        #osuser = get_osuser(request.opensocial_userid, request)
        request.osuser = get_osuser(request.opensocial_userid, request)
        return view_func(request, *args, **kwds)
    return decorate


class OutputLog(object):
    """
    ログ出力クラス

    gsocial/log.py に移植
    """
    _logger = logging.getLogger('gsocial')

    @classmethod
    def debug(cls, message):
        """
        debug用
        """
        cls._logger.debug(message)

    @classmethod
    def info(cls, message):
        """
        info用
        """
        cls._logger.info(message)

    @classmethod
    def error(cls, message):
        """
        error用
        """
        cls._logger.error(message)

    @classmethod
    def warn(cls, message):
        """
        warning用
        """
        cls._logger.warn(message)
