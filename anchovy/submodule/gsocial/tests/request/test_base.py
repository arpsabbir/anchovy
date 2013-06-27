# -*- coding: utf-8 -*-
import unittest
from nose.tools import ok_, eq_
from gsocial.utils.request.base import RequestBase


#class ActivityBaseTests(object):
class ActivityBaseTests(unittest.TestCase):

    def test_init(self):
        target = RequestBase(request=None)
        ok_(target)

    def test_create_request_data(self):
        target = RequestBase(request=None)
        value = target.create_request_data()
        eq_(None, value)

    def test__create_request_data(self):
        target = RequestBase(request=None)
        value = target._create_request_data()
        eq_(None, value)

    def test__create_request_template(self):
        target = RequestBase(request=None)
        value = target._create_request_template()
        eq_(None, value)

