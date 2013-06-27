# -*- coding: utf-8 -*-
"""
gsocial middleware
"""
import threading
import re
import base64
import hashlib
import urllib
import binascii
import hmac
from gsocial.log import Log

from oauth.oauth import OAuthRequest as Request
from oauth.oauth import OAuthError as Error
from oauth import oauth
from oauth.oauth import escape, _utf8_str

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse

from gsocial.http import HttpResponseNotAuthorized, HttpResponseOpensocialRedirect
from gsocial.setting import GREE, GREE_NET
from gsocial.log import Log
from gsocial.set_container import containerdata

from mobilejp.middleware.mobile import get_current_device


oauth2_enable = False
thread_local = None

def set_thread_local_session_id(session_id):
    """
    Set Session ID  on thread local.
    セッションIDをスレッドローカルにセットする
    """
    Log.debug("""
    ##########################################################################
    # set_thread_local_session_id
    ##########################################################################
    """)

    global thread_local
    if thread_local is None:
        thread_local = threading.local()
    thread_local.session_id = session_id

def get_thread_local_session_id():
    """
    Get Session ID of thread local.
    セッションIDをスレッドローカルを取得
    """
    Log.debug("""
    ##########################################################################
    # get_thread_local_session_id
    ##########################################################################
    """)

    global thread_local
    if thread_local:
        return thread_local.session_id
    return None


STR_POST_KEY_VALUES = '_listed'

def _add_post_values_key(key):
    """
    add_post_values_key name create
    """
    return key + STR_POST_KEY_VALUES

def _is_post_values_key(key):
    """
    post_values_key check
    """
    return key.endswith(STR_POST_KEY_VALUES)

def _remove_post_values_key(key):
    """
    $emove_post_values_key
    """
    return  key.split(STR_POST_KEY_VALUES)[0]


class OAuthMiddleware(object):
    """
    Only for OAuth checking.
    OAuth認証だけを行う
    """
    def process_request(self, request):
        """
        process_request
        """
        Log.debug("[Method] process_request ####################")
        Log.debug(request)
        Log.debug("##########################################################################")

        # ignore設定
        if hasattr(settings, 'OAUTH_IGNORE_PATH'):
            ignore_path = settings.OAUTH_IGNORE_PATH
            for path in ignore_path:
                if request.path.startswith(path):
                    return None
        return oauth_signature(request)


class Request2(Request):
    """
    On  get_normalized_parameters,the same key(as like hoge_id = 1&hoge_id = 2 in POST) will
    be identify as one key by using get_normalized_parameters.It is to prepare for failure in Auth.

    get_normalized_parametersにおいて、
    同名のキー（POSTにおけるhoge_id=1&hoge_id=2）が1つにまとめられ、
    Authに失敗するため処置する
    """
    def get_normalized_parameters(self):
        """
        Return a string that contains the parameters that must be signed.
        """
        Log.debug("[Method] get_normalized_parameters")
        params = self.parameters
        try:
            # Exclude the signature if it exists.
            del params['oauth_signature']
        except:
            pass

        # Escape key values before sorting.
        key_values = []
        for key, value in params.iteritems():
            if isinstance(key, basestring) and not _is_post_values_key(key):
                key_values.append((escape(_utf8_str(key)), escape(_utf8_str(value))))
            else:
                try:
                    value = list(value)
                except TypeError, e:
                    assert 'is not iterable' in str(e)
                    key_values.append((escape(_utf8_str(key)), escape(_utf8_str(value))))
                else:
                    if _is_post_values_key(key):
                        key = _remove_post_values_key(key)
                    key_values.extend((escape(_utf8_str(key)), escape(_utf8_str(item)) if isinstance(item, basestring) else item) for item in value)

        # Sort lexicographically, first after key, then after value.
        key_values.sort()
        # Combine key value pairs into a string.
        return '&'.join(['%s=%s' % (k, v) for k, v in key_values])

def create_message(request, params):
    """
    create_message
    """
    Log.debug("[Method] create_message")

    host = request.get_host()
    host = host.split(',')[0]
    base_url = request.is_secure() and 'https://' or 'http://' + host + request.path
    oauth_request = Request2(
        request.method,
        base_url,
        params)
    message = '&'.join((
            oauth.escape(oauth_request.get_normalized_http_method()),
            oauth.escape(oauth_request.get_normalized_http_url()),
            oauth.escape(oauth_request.get_normalized_parameters()),
            ))
    return message

def create_rsa_hash(request, params):
    """
    create_rsa_hash
    """
    Log.debug("[Method] create_rsa_hash")

    message = create_message(request, params)
    return hashlib.sha1(message).digest()

def create_hmac_hash(request, params, oauth_token_secret):
    """
    create_hmac_hash
    """
    Log.debug("[Method] create_hmac_hash")

    message = create_message(request, params)
    shared_key = '%s&%s' % (oauth.escape(settings.CONSUMER_SECRET),
                            oauth.escape(oauth_token_secret))
    hashed = hmac.new(shared_key, message, hashlib.sha1)
    return hashed.digest()

def create_hashed_debug_user_id(request):
    """
    Creates User-id randomly from request.
    Combining HTTP_USER_AGENT and REMOTE_ADDR will create unique id.
    *This is not the decorator.oauth_signature_required will call it.

    requestから、ランダムなユーザーIDを作成する。
    HTTP_USER_AGENTと、REMOTE_ADDRから一意なIDを生成。
    ※デコレータでは無い。oauth_signature_required から呼ばれる。
    """
    Log.debug("[Method] create_hashed_debug_user_id")

    bulk_user_id = request.META.get('HTTP_USER_AGENT')
    hashed_debug_osuser_number = int(hashlib.sha1(bulk_user_id).hexdigest()[5:11], 16)
    hashed_debug_osuser_number %= 100000000
    opensocial_debug_user_id = hashed_debug_osuser_number  + 9900000000
    return str(opensocial_debug_user_id)


def _set_webview_session(request):
    Log.debug("_set_webview_session start")
    Log.debug("session_items before: %s" % request.session.items())
    request.session['is_webview'] = True
    request.session.save()
    Log.debug("session_items after: %s" % request.session.items())
    Log.debug("_set_webview_session end")
    return True


def oauth_signature(request):
    """
    oauth signature authorization
    How it will be proceed
    If debug-mode: "None" will be returned
    If actual-mode:
       if SP,or PC user:
          go to _verify_sign_pc
       if FP:
        go to _verify_mobile

    oauth signature 認証

    処理の流れ
    デバッグモード時: 「None」が返される
    本番モード:
        スマホ,PCユーザーの場合:
        _verify_sign_pc処理へ
        フューチャーフォンユーザーの場合:
        _verify_sign_mobile処理へ
    """


    Log.debug("[Method] oauth_signature")


    #######################################################
    # 1. requestにデバイス情報を生やす
    #######################################################
    is_smartphone = False
    is_featurephone = False

    device = get_current_device()

    if device.is_featurephone:
        is_featurephone = True
    else:
        is_smartphone = True

    if settings.OPENSOCIAL_DEBUG and settings.OPENSOCIAL_SMARTPHONE_DEBUG:
        is_smartphone = True
        is_featurephone = False

    request.is_smartphone = is_smartphone
    request.is_featurephone = is_featurephone
    request.device = device

    # WebViewアプリ情報をapp_user_agentに設定
    # TODO: 複数のプラットフォームに対応する際はapp_user_agentを分岐に変更
    # app_user_agent = request.REQUEST.get('X-GREE-User-Agent', '')
    request.session['app_user_agent'] = device.name
    Log.debug("is_webview:::::: device.is_webview=%s" % device.is_webview)
    Log.debug("is_webview:::::: session.is_webview=%s" % request.session.get('is_webview'))
    if device.is_webview:
        _set_webview_session(request)
#        request.session['is_webview'] = True
#        request.session.save()
    Log.debug("is_webview:::::: session.is_webview=%s" % request.session.get('is_webview'))

    #######################################################
    # 1. End
    #######################################################

        
    # Use this after the authorization
    # 認証後に使おう
    #request.opensocial_viewer_id = str(request.REQUEST.get('opensocial_viewer_id'))
    # Authorizaiton of debug User
    # デバッグユーザーの（空）認証
    if settings.OPENSOCIAL_DEBUG:
        if settings.OPENSOCIAL_DEBUG_USER_ID:
            opensocial_owner_id = settings.OPENSOCIAL_DEBUG_USER_ID
        else:
            opensocial_owner_id = create_hashed_debug_user_id(request)

        opensocial_userid = str(opensocial_owner_id)
        request.session['opensocial_userid'] = opensocial_userid
        request.opensocial_viewer_id = str(opensocial_owner_id)

#        if is_smartphone:
            # for the testing smartphone
            # ローカルスマフォ対応でのテスト用
#            return _verify_sign_pc(request)
        return None

    if request.is_smartphone and not request.path.startswith('/m/appevent/'):
        # authorization of PC user
        # スマホ/PC ユーザーの認証
        return _verify_sign_pc(request)

    else:
        # authorization of mobile user
        # 携帯ユーザーの認証
        return _verify_sign_mobile(request)

def _oauth_reauth_context(request):
    """
    再認証誘導ページヘリダイレクト
    """
    Log.debug("[Method] _oauth_reauth_context")

    if settings.OPENSOCIAL_SANDBOX:
        domain = 'pf-sb.gree.jp'
    else:
        domain = 'pf.gree.jp'
    app_url = 'http://{}{}'.format(settings.SITE_DOMAIN, request.path)
    provider_url = 'http://{}/{}?url={}'.format(domain, settings.APP_ID, urllib.quote(app_url, '~'))
    return RequestContext(request, {
        'message': u'ﾕｰｻﾞｰ認証が失敗しました。もう一度ﾛｸﾞｲﾝしてください。',
        'back_url': provider_url,
    })

def oauth_timeout_response(request):
    """
    For Gree
    """
    request.session.flush()
    ctxt = _oauth_reauth_context(request)
    if request.device.is_ios and re.search(r'^6', request.device.version):
        Log.debug("[Method] oauth_timeout_response ios6 ")
        return HttpResponseForbidden(
                render_to_string('root/auth_redirect.html', ctxt))
    else:
        Log.debug("[Method] oauth_timeout_response ")
        return HttpResponseForbidden(
                render_to_string(settings.SMARTPHONE_ERROR_TEMPLATE, ctxt))

def _get_security_name():
    """
       Creates a key which wil be used in Cookie-security-check
       If there is no  "SECURITY_COOKIE_NAME" in settings.py,this will
       be option.
       cokkieによるセキュリティチェックのkey生成
       settings.pyに「SECURITY_COOKIE_NAME」がなければoptionになる
    """
    Log.debug("[Method] _get_security_name")

    return getattr(settings, 'SECURITY_COOKIE_NAME', 'option')

def _security_check(request, session_id):
    """
    Security check using cookie
    cookieによるセキュリティチェック
    """

    #リクエストサービスのコールバックにcookieチェックは不要
    if settings.GREE_REQUEST_API and request.path == reverse(settings.GREE_REQUEST_API_HEADER):
        return True

    from mobilejp.middleware.mobile import get_current_device
    device = get_current_device()
    Log.debug("_security_check device.is_webview %s" % device.is_webview)
    if device.is_webview:
        Log.debug("[Method] _security_check webview Pass")
        return True

    Log.debug("[Method] _security_check ")

    ua = request.META.get('HTTP_USER_AGENT', None)
    if ua is None:
        return False

    security_name = request.COOKIES.get(_get_security_name(), u'')
    m = hashlib.md5()
    m.update(ua)
    m.update(str(session_id))

    Log.debug("[Method] _security_check security_name: %s", security_name)
    Log.debug("[Method] _security_check m.hexdigest: %s", m.hexdigest())

    return m.hexdigest() == security_name

def _security_set(request, response):
    """
    Set the key to Cookie,
    which will be invalid in 30 min.
    cokkieに鍵をセットする
    30分でcookieは消える
    """
    Log.debug("[Method] _security_set")

    ua = request.META.get('HTTP_USER_AGENT', None)
    if ua is None:
        return

    #security_name = request.COOKIES.get(_get_security_name(), u'default')
    m = hashlib.md5()
    m.update(ua)
    m.update(str(request.session_id))
    val = m.hexdigest()
    response.set_cookie(_get_security_name(), val, max_age=30*60, path='/')

def _oauth_rekey(request, webview_flag=False):
    """
    Reconfigure the keys for Oauth
    oauth周りのキーを再設定
    """

    Log.debug("[Method] _oauth_rekey")

    Log.debug("[Method] _oauth_rekey webview_flag:%s" % webview_flag)

    if request.REQUEST.get('opensocial_viewer_id', None):
        Log.debug("[Method] _oauth_rekey flush session")
        request.session.flush()
        request.session['opensocial_userid'] = request.REQUEST['opensocial_viewer_id']
        request.session['oauth_token'] = request.REQUEST['oauth_token']
        request.session['oauth_token_secret'] = request.REQUEST['oauth_token_secret']
        request.session.set_expiry(60 * 30)
    if webview_flag:
        Log.debug("[Method] _oauth_rekey _set_webview_session")
        _set_webview_session(request)


    # Send information about WebView application to app_usr_agent
    # WebViewアプリ情報をapp_user_agentに
    # app_user_agent = request.REQUEST.get('X-GREE-User-Agent', '')

#いらない
#    request.session['app_user_agent'] = request.device.name
#    if request.device.is_webview:
#        request.session['is_webview'] = True

    request.session_id = request.session.session_key
    request.session.save()
    # display "the authorization success screen"
    # 認証成功画面を表示
    ctx = RequestContext(request, {
        'scid': request.session_id,
        'next_path': request.path,
        'is_webview': request.device.is_webview,
        'get_dict': request.GET,
        'post_dict': request.POST,
    })

    device = get_current_device()

    if device.is_webview:
        return None

    res = render_to_response(settings.SMARTPHONE_AUTH_SUCCESS_TEMPLATE, ctx)
    res.set_cookie(settings.SESSION_COOKIE_NAME, request.session_id)
    # check again
    # 心配なのでもう一つチェック
    _security_set(request, res)
    return res

def _verify_sign_query(request):
    """
    Checking parameter
    output:
       Usualy:None
       When there is a problem: raise
    パラメータ認証

    output
        正常時: None
        異常時: raise
    """
    Log.debug("[Method] _verify_sign_query")

    auth_string = request.META.get('QUERY_STRING', '')
    if not auth_string:
        raise
    Log.debug("[Method] _verify_sign_query not auth_string End")

    params = {}
    remote_hash = None
    for param in auth_string.split('&'):
        (key, value) = param.strip().split('=', 1)
        value = value.strip('"').encode('utf-8')

        if key == 'oauth_signature':
            remote_hash = base64.decodestring(urllib.unquote(value))
        elif key and key != 'OAuth realm':
            params[key] = value

    if not remote_hash:
        raise

    Log.debug("[Method] _verify_sign_query remote_hash End")

    oauth_token_secret = params.get('oauth_token_secret', '')

    # Some container need query parameter only to create base_string
    # while some need postdata as well,so you create both hash pattern.
    # As one of them matches,checking will be passed.

    # コンテナによって、base_stringを作成するのにクエリパラメータのみを使うもの、
    # postdataも含めるものがあるので、両方のパターンのハッシュを作り
    # どちらかがマッチすれば認証OKとする。

    encoding = request.encoding
    if not encoding:
        encoding = 'utf-8'

    for key, value in request.GET.items():
        if key and key != 'oauth_signature':
            params[key] = value.encode(encoding)
    # create hash by only using query parameter.
    # クエリパラメータのみを使ってハッシュを作成
    local_hash1 = create_hmac_hash(request, params, oauth_token_secret)
    # create hash by using the parameter which contain POSTDATA
    # POSTDATAも含めたパラメータを使ってハッシュを作成
    for key, value in request.POST.copy().items():
        if key and key != 'oauth_signature':
            params[key] = value.encode(encoding)

    local_hash2 = create_hmac_hash(request, params, oauth_token_secret)

    # Verify that the locally-built value matches the value
    # from the remote server
    ###### IF local_hash1 != remote_hash and local_hash2 != remote_hash START ######
    Log.debug("[Method] _verify_sign_query local_hash1: %s" % local_hash1)
    Log.debug("[Method] _verify_sign_query local_hash2: %s" % local_hash2)
    Log.debug("[Method] _verify_sign_query remote_hash: %s" % remote_hash)

    if local_hash1 != remote_hash and local_hash2 != remote_hash:
        raise

    Log.debug("[Method] _verify_sign_query remote_hash == local_hash1 & local_hash12")

    request.opensocial_userid = str(request.GET['opensocial_viewer_id'])
    request.opensocial_viewer_id = str(request.GET['opensocial_viewer_id'])
    return None


def _is_need_oauth_check_header(request):
    """
    Decide whether oauth_check_header is needed
    output:
       True:Needed
       False: Unneeded

    oauth_check_headerが必要かを判定

    output
        True: 必要
        False: 不必要
    """

    must_path_list = getattr(settings, 'OAUTH_MUST_PATH_HEADER', [])
    path = request.path
    for p in must_path_list:
        if path.startswith(p):
            Log.debug("[Method] _is_need_oauth_check_header:: return True")
            return True

    Log.debug("[Method] _is_need_oauth_check_header:: return False")
    return False

def _is_need_oauth_check_query(request):
    """
    oauth_check_queryが必要かを判定

    output
        True: 必要
        False: 不必要
    """
    Log.debug("[Method] _is_need_oauth_check_query")

    must_path_list = getattr(settings, 'OAUTH_MUST_PATH_QUERY', [])
    path = request.path
    for p in must_path_list:
        if path.startswith(p):
            return True

    return False

def _verify_sign_pc(request):
    """
    Oauth Login checking for SP/PC

    return value
       authorization ok :None

    Session ID will try to get REQUEST from COOKIES as well.
    On Safari,you won`t be able to use COOKIES at the first page.
    Get session ID from cookie.
    session_id_from_request = False

    SP/PC用のログインOAUTH認証

    返り値
        認証ok時: None


    セッションIDはCOOKIESからもREQUESTからも取得しようとする。
    Safariの制限で初ページはCOOKIESを使えない
    クッキーからセッションID取得
    """
    Log.debug("[Method] _verify_sign_pc")

    #Log.debug(request)
    #session_id_from_request = False
    session_id = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)

    from mobilejp.middleware.mobile import get_is_webview

    #need certificate check
    # certificateチェックが必要です。
    request.session_id = request.session.session_key
    if not request.path.startswith('/m/'):
        return None

    user_agent = request.META.get('HTTP_USER_AGENT', '')
    if not request.is_smartphone:
        ctxt = RequestContext(request, {
            'message': 'ﾕｰｻﾞｰ認証が失敗しました。もう一度ﾛｸﾞｲﾝしてください。',
        })
        return render_to_response(settings.SMARTPHONE_ERROR_BLOCK_TEMPLATE, ctxt)

    #TODO webviewはチェックしない
    if get_is_webview():
        Log.debug("webview_check_pass")
        _oauth_rekey(request, True)
        if request.session.get('opensocial_userid'):
            request.opensocial_userid    = request.session.get('opensocial_userid')
            request.opensocial_view_id   = request.session.get('opensocial_userid')
            request.opensocial_viewer_id = request.session.get('opensocial_userid')

        return None

    if _is_need_oauth_check_header(request):
        try:
            return _verify_sign_header(request)
        except:
            res = oauth_timeout_response(request)
            res.delete_cookie(settings.SESSION_COOKIE_NAME)
            res.delete_cookie(_get_security_name())
            return res

    Log.debug("[Method] _is_need_oauth_check_header(request) END ")

    if _is_need_oauth_check_query(request):
        try:
            return _verify_sign_query(request)
        except:
            res = oauth_timeout_response(request)
            res.delete_cookie(settings.SESSION_COOKIE_NAME)
            res.delete_cookie(_get_security_name())
            return res

    Log.debug("[Method] _is_need_oauth_check_query(request) END ")


    if not (settings.GREE_REQUEST_API and request.path == reverse(settings.GREE_REQUEST_API_HEADER)):
        if request.REQUEST.get('opensocial_app_id', None):

            try:
                _verify_sign_query(request)
                #TODO webviewはチェックしない
                if get_is_webview():
                    _oauth_rekey(request, True)
                    return None
                else:
                    return _oauth_rekey(request)
            except oauth.OAuthError:
                return oauth_timeout_response(request)
            except:
                res = oauth_timeout_response(request)
                res.delete_cookie(settings.SESSION_COOKIE_NAME)
                res.delete_cookie(_get_security_name())
                return res

    Log.debug("[Method] _verify_sign_pc IF request.REQUEST.get('opensocial_app_id', None) END ")

    #if SessionID is valid,call view_func and finish.
    # 有効セッションIDの場合、view_funcを呼び出して終わる
    if not session_id:
        Log.debug("[Method] _verify_sign_pc not session_id")
        return oauth_timeout_response(request)


    Log.debug("session_id %s" % session_id)
    engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    request.session = engine.SessionStore(session_id)

    if not _security_check(request, session_id):
        # start checking
        # 認証に回す
        res = oauth_timeout_response(request)
        res.delete_cookie(settings.SESSION_COOKIE_NAME)
        res.delete_cookie(_get_security_name())
        return res
    Log.debug("[Method] _verify_sign_pc not _security_check(request, session_id) END")

#    engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
#    request.session = engine.SessionStore(session_id)
    if 'opensocial_userid' in request.session:
        if request.session.get_expiry_age() <= 0:

            #Can not authorized with SessionID
            # セッションIDで認証できない
            request.session.flush()
            Log.debug("[Method] _verify_sign_pc expiry_age() < 0 session clear")
        else:
            #Authorization successed.Doesn`t need certificate check.
            # 認証成功！certificateチェックが要らない！
            request.opensocial_userid = request.session['opensocial_userid']
            request.opensocial_view_id = request.session['opensocial_userid']
            request.opensocial_viewer_id = request.session['opensocial_userid']
            request.session_id = request.session.session_key

            # set_thread_local_session_id(request.session_id)
            # If OAuth authorization has expired and proceed the
            # auto-authorization,this will redirect to the page
            # the User wanted to see.

            # set_thread_local_session_id(request.session_id)
            # OAuth認証切れで自動認証を行った場合
            # ユーザの閲覧したかった元ページへ移動させる


            #gree request対象のpathには oauth middlewareを無視する
            if settings.GREE_REQUEST_API and request.path == reverse(settings.GREE_REQUEST_API_HEADER):
                return None

            next_path = request.POST.get('next_path', '')
            if next_path and request.path in ['/m/', '/m/home/']:
                Log.debug("[Method] _verify_sign_pc next_path")

                return HttpResponseOpensocialRedirect(next_path)
            return None

    return oauth_timeout_response(request)


def generate_post_hash(request, encoding):
    """
    fix: POST same key in multi value
    """
    Log.debug("[Method] generate_post_hash")

    post_param = {}
    for key, value in request.POST.lists():
        if len(value) == 1:
            value = ','.join(value)
            if key and key != 'oauth_signature':
                post_param[key] = value.encode(encoding)
        else:
            #if list
            # リストである場合
            for i, v in enumerate(value):
                try:
                    value[i] = int(v)
                except TypeError:
                    value[i] = v.encode(encoding)
            post_param[_add_post_values_key(key)] = value
    return post_param

def _verify_sign_mobile(request):
    """
    Oauth checking process for FP

    output
     authorization ok :None
     with error : redirect to request.get_full_path
     else: raise

    FP用のOAUTH認証処理

    output
        認証ok: None
        error時: request.get_full_pathへのリダイレクト
        それ以外: raise

    """
    Log.debug("[Method] _verify_sign_mobile")

    request.opensocial_container = containerdata
#    header_params = {}
#    oauth_signature = request.REQUEST.get('oauth_signature', None)
    auth_string = ''
    try:
        auth_string = request.META.get('HTTP_AUTHORIZATION', '')
        auth_string = auth_string.replace('OAuth ', '')
        Log.debug('HTTP_AUTHORIZATION', auth_string)
        params = {}
        remote_hash = False
        for param in auth_string.split(','):
            Log.debug('param', param)
            (key, value) = param.strip().split('=', 1)
            value = value.strip('"').encode('utf-8')
            if key == 'oauth_signature':
                remote_hash = base64.decodestring(urllib.unquote(value))
            elif key and key != 'OAuth realm' and key != 'realm':
                params[key] = value
        Log.debug('params', params)
        if not remote_hash:
            raise

        oauth_token_secret = params.get('oauth_token_secret', '')

        # Some container only need query parameter to create base_string
        # while some need postdata as well,so you create both hash pattern.
        # As one of them matches,checking will be passed.

        # コンテナによって、base_stringを作成するのにクエリパラメータのみを使うもの、
        # postdataも含めるものがあるので、両方のパターンのハッシュを作り
        # どちらかがマッチすれば認証OKとする。

        encoding = request.encoding
        if not encoding:
            encoding = 'utf-8'

        for key, value in request.GET.items():
            if key and key != 'oauth_signature':
                params[key] = value.encode(encoding)
        Log.debug('params', params)

        #local_hash1 = local_hash2 = u''
        #create hash by only using query parameter.
        # クエリパラメータのみを使ってハッシュを作成
        local_hash1 = create_hmac_hash(request, params, oauth_token_secret)
        #create hash with using parameter contain POSTDATA.
        # POSTDATAも含めたパラメータを使ってハッシュを作成
        post_param = generate_post_hash(request, encoding)

        params.update(post_param)
        local_hash2 = create_hmac_hash(request, params, oauth_token_secret)

        host = request.get_host()
        host = host.split(',')[0]
        base_url = request.is_secure() and 'https://' or 'http://' + host + request.path

        Log.info('base_url', base_url)
        for k, v in params.iteritems():
            if isinstance(v, basestring):
                Log.info('Check k and v.decode(encoding) of params.iteritems()', [k, v.decode(encoding)])
            else:
                Log.info('Check k and v of params.iteritems()', [k, v])
        Log.info('raw', request.raw_post_data)
        Log.info('remote_hash', binascii.b2a_base64(remote_hash)[:-1])
        Log.info('local_hash1', binascii.b2a_base64(local_hash1)[:-1])
        Log.info('local_hash2', binascii.b2a_base64(local_hash2)[:-1])

        Log.info('local_hash1 == remote_hash ?', (local_hash1 == remote_hash))
        Log.info('local_hash2 == remote_hash ?', (local_hash2 == remote_hash))

        if local_hash1 != remote_hash and local_hash2 != remote_hash:
            raise

    except Error, err:
        Log.error('oauth error', err.message)
        return HttpResponseNotAuthorized(request.get_full_path())
    except:
        import sys
        exceptionType, exceptionValue, exceptionTraceback = sys.exc_info()
        Log.error('Invalid OAuth Signature.', [exceptionType, exceptionValue])
        Log.error('HTTP_AUTHORIZATION', auth_string)
        return HttpResponseNotAuthorized(request.get_full_path())
    else:
        opensocial_owner_id = request.REQUEST.get('opensocial_owner_id', None)
        if opensocial_owner_id is not None:
            request.opensocial_userid = str(opensocial_owner_id)
            request.opensocial_viewer_id = str(opensocial_owner_id)
        return None

def _verify_sign_header(request):
    """
    OAuth checking of header
    output
      authorization ok :None
      else: raise

    ヘッダーのOAUTH認証

    output
        認証ok: None
        それ以外: raise
    """
    Log.debug("[Method] _verify_sign_header")

    request.opensocial_container = containerdata
    #下記つかってないのでコメントアウト
    #header_params = {}
    #oauth_signature = request.REQUEST.get("oauth_signature", None)

    auth_string = request.META.get('HTTP_AUTHORIZATION',"")
    auth_string = auth_string.replace('OAuth ',"")
    Log.debug('HTTP_AUTHORIZATION', auth_string)
    params = {}
    remote_hash = False
    for param in auth_string.split(','):
        Log.debug('param', param)
        (key, value) = param.strip().split('=', 1)
        value = value.strip('"').encode('utf-8')
        if key == 'oauth_signature':
            remote_hash = base64.decodestring(urllib.unquote(value))
        elif key and key != 'OAuth realm' and key != 'realm':
            params[key] = value
    Log.debug('params', params)
    if not remote_hash:
        raise

    oauth_token_secret = params.get('oauth_token_secret', '')

    # Some container only need query parameter to create base_string
    # while some need postdata as well,so you create both hash pattern.
    # As one of them matches,checking will be passed.
    # コンテナによって、base_stringを作成するのにクエリパラメータのみを使うもの、
    # postdataも含めるものがあるので、両方のパターンのハッシュを作り
    # どちらかがマッチすれば認証OKとする。
    encoding = request.encoding
    if not encoding:
        encoding = 'utf-8'

    for key, value in request.GET.items():
        if key and key != 'oauth_signature':
            params[key] = value.encode(encoding)
    Log.debug('params', params)

#    local_hash1 = local_hash2 = u''
    #create hash by only using query parameter.
    # クエリパラメータのみを使ってハッシュを作成
    local_hash1 = create_hmac_hash(request, params, oauth_token_secret)
    # create hash with using parameter contain POSTDATA
    # POSTDATAも含めたパラメータを使ってハッシュを作成
    post_param = generate_post_hash(request, encoding)

    params.update(post_param)
    local_hash2 = create_hmac_hash(request, params, oauth_token_secret)

    host = request.get_host()
    host = host.split(',')[0]
    base_url = request.is_secure() and 'https://' or 'http://' + host + request.path

    Log.info('base_url', base_url)
    for k, v in params.iteritems():
        if isinstance(v, basestring):
            Log.info('Check k and v.decode(encoding) of params.iteritems()', [k, v.decode(encoding)])
        else:
            Log.info('Check k and v of params.iteritems()', [k, v])

    Log.info('raw', request.raw_post_data)
    Log.info('remote_hash', binascii.b2a_base64(remote_hash)[:-1])
    Log.info('local_hash1', binascii.b2a_base64(local_hash1)[:-1])
    Log.info('local_hash2', binascii.b2a_base64(local_hash2)[:-1])

    Log.info('local_hash1 == remote_hash ?', (local_hash1 == remote_hash))
    Log.info('local_hash2 == remote_hash ?', (local_hash2 == remote_hash))

    if local_hash1 != remote_hash and local_hash2 != remote_hash:
        raise

    opensocial_owner_id = request.REQUEST.get('opensocial_owner_id', None)
    if opensocial_owner_id is not None:
        request.opensocial_userid = str(opensocial_owner_id)
        request.opensocial_viewer_id = str(opensocial_owner_id)

    return None
