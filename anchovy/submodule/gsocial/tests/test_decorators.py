# -*- coding: utf-8 -*-
"""
gsocial decorator test
"""

import threading
from nose.tools import eq_

from django.test import TestCase
from gsocial.utils.base import GsocialCache
from django.template import loader
from django.conf import settings
from django.test.client import RequestFactory

from gsocial.decorators import *

class TestGrobalModule(TestCase):
    """
    ModuleTest
    """

    def test_set_thread_local_session_id(self):
        THREAD_LOCAL = None
        test_mes = "gggggggggggggg"
        set_thread_local_session_id(test_mes)

    def test_get_thread_local_session_id(self):
        THREAD_LOCAL = None
        test_mes = "gggggggggggggg"
        set_thread_local_session_id(test_mes)
        eq_(get_thread_local_session_id(), test_mes)

#    def test_SMARTPHOPNE_RE(self):
#        eq_(SMARTPHOPNE_RE, re.compile(r'Android|iPhone|iPad'))

    def test_create_message(self):
        rf = RequestFactory()
        request  =  rf.get('/test/')
        res = "GET&http%3A%2F%2Ftestserver%2Ftest%2F&"
        eq_(create_message(request, {}), res)

    def test_create_rsa_hash(self):
        rf = RequestFactory()
        request  =  rf.get('/test/')
        res = "\xad\\\xc3\x10Hf\x12\x16W\x07\x97\xf8%\xfa\xa0\x82\xb3\xee4l"
        eq_(create_rsa_hash(request, {}), res)

 
    def test_create_hmac_hash(self):
        rf = RequestFactory()
        request  =  rf.get('/test/')
        oauth_token_secret = "xxxxxxxxxxx"
        res = "\xfa\x80\xb1\x0c\xd1\xc2\xc9\xe2\xe8\x89M\xd3!8\xdb\x17\xc2a\x0c\x8d"
        eq_(create_hmac_hash(request, {}, oauth_token_secret), res)

    def test_sighened_request(self):
        """
        TODO decoratorsのテスト書き方分からない
        """
        signed_request("view")

    def test_create_hashed_debug_user_id(self):
        rf = RequestFactory()
        request  =  rf.get('/test/')
        request.META['HTTP_USER_AGENT'] = "ggggggg"
        assert(create_hashed_debug_user_id(request) != None )
        assert(int(create_hashed_debug_user_id(request)) > 1)

    def test_oauth_signature_required(self):
        """
        TODO decoratorsのテスト書き方分からない
        """
        oauth_signature_required("view")

    def test_require_osuser(self):
        """
        TODO decoratorsのテスト書き方分からない
        """
        require_osuser("view")


class TestRequest2(TestCase):
    """
    Request2のテスト
    """

    def test_get_normalized_parameters(self):
        obj = Request2()
        self.parameters = {'ggggg':'ggggggggggggg'}
        eq_(obj.get_normalized_parameters(), '')


