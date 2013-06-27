# -*- coding: utf-8 -*-

from nose.tools import eq_

from django.test import TestCase
from gsocial.utils.base import GsocialCache
from django.template import loader
from django.conf import settings
from django.test.client import RequestFactory

from gsocial.oauth_middleware import *
from gsocial.oauth_middleware import _add_post_values_key, _is_post_values_key,\
    _remove_post_values_key, _oauth_reauth_context, _verify_sign_pc, \
    _verify_sign_mobile

class TestGrobalModule(TestCase):
    """
    ModuleTest
    """
    def setUp(self):
        rf = RequestFactory()
        request  =  rf.get('/test/')

    def test_set_thread_local_session_id(self):
        THREAD_LOCAL = None
        test_mes = "gggggggggggggg"
        set_thread_local_session_id(test_mes)

    def test_get_thread_local_session_id(self):
        THREAD_LOCAL = None
        test_mes = "gggggggggggggg"
        set_thread_local_session_id(test_mes)
        eq_(get_thread_local_session_id(), test_mes)

    def test_add_post_values_key(self):
        key_name = "gggg"
        res = key_name + STR_POST_KEY_VALUES
        eq_(_add_post_values_key(key_name), res)

    def test_is_post_values_key(self):
        key_name = "gggg"
        res = key_name + STR_POST_KEY_VALUES
        eq_(_is_post_values_key(res), True)

    def test_remove_post_values_key(self):
        key_name = "gggg"
        eq_(_remove_post_values_key(key_name), key_name)

    def test_create_hashed_debug_user_id(self):
        rf = RequestFactory()
        request  =  rf.get('/test/')
        request.META['HTTP_USER_AGENT'] = "ggggggg"
        assert(create_hashed_debug_user_id(request) != None )
        assert(int(create_hashed_debug_user_id(request)) > 1)

    def test_oauth_signature(self):
        """
        test
        TODO 外部モジュールインストールしなければならないのでテスト不可
        """
        #request.META['HTTP_USER_AGENT'] = "ggggggg"
        #eq_(oauth_signature(request), None)
        pass

    def test__oauth_reauth_context(self):
        """
        test
        """
        pass
#        from django.template import RequestContext
#        rf = RequestFactory()
#        request  =  rf.get('/test/')
#        eq_(_oauth_reauth_context(request).__class__, RequestContext)

    def test_oauth_timeout_response(self):
        """
        test
        """
        pass
        #rf = RequestFactory()
        #request = rf.get('/test/')
        #request.session.flush = None
        #eq_(oauth_timeout_response(request).__class__, RequestContext)


    def test__verify_sign_pc(request):
        """
        session周りの偽装方法を後で考える
        """
        #rf = RequestFactory()
        #request = rf.get('/test/')
        #request.session  =  {}
        #request.session.session_key  =  'bar'
        #settings.SESSION_URL_KEY_NAME = "go"
        #eq_(_verify_sign_pc(request))

    def test_generate_post_hash(self):
        """
        test
        """
        rf = RequestFactory()
        request = rf.get('/test/')

        generate_post_hash(request, "UTF8")

    def test__verify_sign_mobile(self):
        """
        test
        """
        rf = RequestFactory()
        request = rf.get('/test/')
        #_verify_sign_mobile(request)

class TestOAuthMiddleware(TestCase):
    def test_process_request(self):
        """
        test
        get_current_deviceインポーーとできないので動かない
        """
        pass
        #rf = RequestFactory()
        #request = rf.get('/test/')
        #OAuthMiddleware().process_request(request)


class TestRequest2(TestCase):
    """
    test
    """
    def test_get_normalized_parameters(self):
        """
        test
        """
        tmp = Request2()
        tmp.parameters = {'g':1, 't':2}
        res = "g=1&t=2"
        eq_(tmp.get_normalized_parameters(), res)

