# -*- coding: utf-8 -*-
from nose.tools import eq_, ok_
from gsocial.utils.base import escape, get_normalized_http_url, OAuthSignatureMethod_HMAC_SHA1_OPENSOCIAL, get_session_data, GsocialCache


class Test_utils_base():

    def test_escape(self):
        ex = escape('~test~')
        eq_('~test~', ex)

    # TODO : テストできない
    def test_normalized_http_url(self):
        ok_(True)


class Test_OAuthSignatureMethod_HMAC_SHA1_OPENSOCIAL():

    def test_get_name(self):
        obj = OAuthSignatureMethod_HMAC_SHA1_OPENSOCIAL()
        ex = obj.get_name()
        eq_('HMAC-SHA1', ex)

    # TODO : テストできない
    def test_build_signature_base_string(self):
        ok_(True)

    # TODO : テストできない
    def test_build_signature(self):
        ok_(True)


class Test_get_session_data():

    # TODO : テストできない
    def Test_get_session_data(self):
        ok_(True)


class Test_GsocialCache():

    CACHE_KEY = 'people:/people/1111/@self:1111'
    CACHE_VALUE1 = 'test_value1'
    CACHE_VALUE2 = 'test_value2'

    def test_set_cache(self):
        cache_key = self.CACHE_KEY
        cache_value = self.CACHE_VALUE1
        GsocialCache.set_cache(cache_key, cache_value, timeout=5)

    def test_get_cache(self):
        cache_key = self.CACHE_KEY
        cache_value = self.CACHE_VALUE1

        # セットする
        GsocialCache.set_cache(cache_key, cache_value, timeout=5)
        # 取得する
        result = GsocialCache.get_cache(cache_key)
        eq_('test_value1', result)

#        # 新しいvalueを再度セット（上書き）し、正常に取得できるか確認
#        cache_value = self.CACHE_VALUE2
#        GsocialCache.set_cache(cache_key, cache_value)
#        # 取得する
#        result = GsocialCache.get_cache(cache_key)
#        eq_('test_value2', result)

    def test_delete_cache(self):
        cache_key = self.CACHE_KEY
        cache_value = self.CACHE_VALUE1

        # セットする
        GsocialCache.set_cache(cache_key, cache_value, timeout=5)
        # 取得する
        result = GsocialCache.get_cache(cache_key)
        eq_('test_value1', result)

        # 削除する
        GsocialCache.delete_cache(cache_key)
        # 取得する
        result = GsocialCache.get_cache(cache_key)
        eq_(None, result)
