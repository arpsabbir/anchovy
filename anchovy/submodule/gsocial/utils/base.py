# -*- coding: utf-8 -*-
"""
"""
import hashlib
import urlparse
import hmac
import binascii
import urllib
from oauth import oauth

from django.core.cache import cache
from django.conf import settings

from gsocial.setting import DEFALT_CACHE_TIMEOUT
from gsocial.log import Log
from gsocial.exceptions import SessionError


def escape(s):
    """
    Escape a URL including any /.
    """
    return urllib.quote(s, safe='~')


def get_normalized_http_url(url):
    """
    Parses the URL and rebuilds it to be scheme://host/path.
    """
    parts = urlparse.urlparse(url)
    scheme, netloc, path, params = parts[:4]
    # Exclude default port numbers.
    if scheme == 'http' and netloc[-3:] == ':80':
        netloc = netloc[:-3]
    elif scheme == 'https' and netloc[-4:] == ':443':
        netloc = netloc[:-4]
    if params:
        return '%s://%s%s;%s' % (scheme, netloc, path, params)
    else:
        return '%s://%s%s' % (scheme, netloc, path)


# oauth
class OAuthSignatureMethod_HMAC_SHA1_OPENSOCIAL(oauth.OAuthSignatureMethod):
    """
    モバゲのアバターAPIがURLに;(セミコロン)を含むため、
    oauthのシグネチャ生成がうまく動かないものを動くようにしたもの
    """
    def get_name(self):
        return 'HMAC-SHA1'

    def build_signature_base_string(self, oauth_request, consumer, token):
        sig = (
            escape(oauth_request.get_normalized_http_method()),
            escape(get_normalized_http_url(oauth_request.http_url)),
            escape(oauth_request.get_normalized_parameters()),
        )

        key = '%s&' % escape(consumer.secret)
        if token:
            key += escape(token.secret)
        raw = '&'.join(sig)
        return key, raw

    def build_signature(self, oauth_request, consumer, token):
        """
        Builds the base signature string.
        """
        key, raw = self.build_signature_base_string(oauth_request, consumer,
            token)

        # HMAC object
        try:
            hashed = hmac.new(key, raw, hashlib.sha1)
        except:
            import sha # Deprecated
            hashed = hmac.new(key, raw, sha)

        # Calculate the digest base 64
        return binascii.b2a_base64(hashed.digest())[:-1]


# container
def get_session_data(request):
    """
    セッションIDから認証情報を取得
    """
    session_id = request.session_id
    Log.debug('Check request.session.', session_id)

    if session_id is None:
        session_id = request.REQUEST.get(settings.SESSION_URL_KEY_NAME, None)
        Log.debug('Check REQUEST SESSION', session_id)

    if session_id is None:
        session_id = request.COOKIES.get(settings.SESSION_COOKIE_NAME, None)
        Log.debug('Check COOKIES SESSION', session_id)

    Log.debug('Check session_id', session_id)

    if session_id is not None:
        engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
        request.session = engine.SessionStore(session_id)
        session_data = {}
        Log.debug('Check request.session.session_key.',
                  request.session.session_key)
        if not 'oauth_token' in request.session:
            raise SessionError('"oauth_token" not in key.')
        Log.debug('Check request.session[\'oauth_token\'].',
                  request.session['oauth_token'])
        if not 'oauth_token_secret' in request.session:
            raise SessionError('"oauth_token_secret" not in key.')
        Log.debug('Check request.session[\'oauth_token_secret\'].',
                  request.session['oauth_token_secret'])

        session_data['oauth_token'] = request.session['oauth_token']
        session_data['oauth_token_secret'] = request.session['oauth_token_secret']
        Log.debug('Check session_data.', session_data)

        return session_data

    return None


class GsocialCache(object):
    """
    共通キャッシュクラス

    キャッシュのキーはAPI毎のpathを利用する
    （pathは、PeopleAPIの場合
    「path = '/people/%s/@self' % userid」という形になっているため）

    pathが被ってしまう場合は、カスタマイズしたキーを作成する
    （例「cache_key = path + ':all_friend'」など）
    """

    @classmethod
    def set_cache(cls, cache_key, cache_value, timeout=None):
        """
        キャッシュにセットする

        アプリ側のsettingsのtimeoutがあれば使う
        なければgsocialのsettingのtimeoutを使う
        """
        if timeout == None:
            # ここは普通のif文に変更した方がよいかも
            try:
                timeout = settings.GSOCIAL_CACHE_TIMEOUT
            except AttributeError:
                Log.info('GSOCIAL_CACHE_TIMEOUT isn\'t in settings.', timeout)
                timeout = DEFALT_CACHE_TIMEOUT


        Log.debug('Check timeout.', timeout)
        cache.set(cache_key, cache_value, timeout)

    @classmethod
    def get_cache(cls, cache_key):
        """
        キャッシュから取得する
        """
        return cache.get(cache_key)

    @classmethod
    def delete_cache(cls, cache_key):
        """
        キャッシュを削除する
        """
        cache.delete(cache_key)
