# -*- coding: utf-8 -*-
import unittest
import requests
import mock
from mock import patch
from nose.tools import *


class InspectionGreeTests(unittest.TestCase):
    def _getTarget(self):
        from gsocial.utils.inspection.gree import InspectionGree
        res =  requests.Response()
        return InspectionGree(res)

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get_cache_key(self):
        res = self._getTarget()._get_cache_key(1111)
        eq_(res, 'Inspection:1111')

    def test_api_path(self):
        method = "POST"
        text_id = "1111"
        path = '/api/rest/inspection/@app'
        eq_(self._getTarget()._api_path(method, text_id), path)

        method = "PUT"
        path = '/api/rest/inspection/@app/' + str(text_id)
        eq_(self._getTarget()._api_path(method, text_id), path)

        method = "GET"
        path = '/inspection/@app/' + str(text_id)
        eq_(self._getTarget()._api_path(method, text_id), path)

        method = "DELETE"
        path = '/inspection/@app/' + str(text_id)
        eq_(self._getTarget()._api_path(method, text_id), path)
