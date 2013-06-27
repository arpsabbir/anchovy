# -*- coding: utf-8 -*-
import unittest
import requests
import mock
from mock import patch
from nose.tools import *

class MessageGreeTests(unittest.TestCase):

    def _getTarget(self):
        from gsocial.utils.message.gree import MessageGree
        return MessageGree()

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_send_list(self):
        tmp_list= range(1,35)
        res_1 = range(1,21)
        res_2 = range(21,35)
        res = self._getTarget()._send_list(tmp_list)
        eq_(res[0], res_1) 
        eq_(res[1], res_2) 



