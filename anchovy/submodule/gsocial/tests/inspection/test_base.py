# -*- coding: utf-8 -*-
import unittest
import requests
import mock
from mock import patch
from nose.tools import *

class InspectionBaseTests(unittest.TestCase):

    def _getTarget(self):
        from gsocial.utils.inspection.base import InspectionBase
        res =  requests.Response()
        return InspectionBase(res)

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get_cache_key(self):
        self._getTarget()._get_cache_key

    def test_api_path(self):
        self._getTarget()._api_path

    def test_api_request(self):
        self._getTarget()._api_request

