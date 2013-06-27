# -*- coding: utf-8 -*-
import unittest
import requests
import mock
from mock import patch
from nose.tools import *


class PaymentBaseTests(unittest.TestCase):

    def _getTarget(self):
        from gsocial.utils.payment.base import PaymentBase 
        res =  requests.Response()
        return PaymentBase(res)

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)


#    @patch("paymentbase.get_mobilepaydata", "5555")
    def test_2(self):
        ts  = self._getTarget()
        ts.test_2 = mock.Mock(name = "method")
        ts.test_2.return_value = 222222
        ts.test_2()
        eq_(222222,ts.test_2(),"Test gggggggggg")
#        print PaymentBase().get_mobilepaydata()

    def test_get_mobilepayment(self):
        cls = self._getTarget()
        eq_(None, cls.get_mobilepaydata(1, {}))

    def test_create_paydata(self):
        item_id = 1
        item_name = "アイテム名"
        item_point = 100
        item_description = "アイテム説明文"
        item_image_url = "アイテム画像のURL"
        callback_url = "コールバックURL"
        finish_url = "購入完了URL"
        item_message = "メッセージ(GREEのみ) default=''"
        item_quantity = 1
        is_test = False

        cls = self._getTarget()
        #res = cls._create_paydata(item_id, item_name, item_point, 
        #item_description, item_image_url, 
        #callback_url, finish_url, item_message, item_quantity, is_test)
        res = cls._create_paydata()
        eq_(None, res)

    def test_request_payment(self):
        item_id = 1
        item_name = "アイテム名"
        item_point = 100
        item_description = "アイテム説明文"
        item_image_url = "アイテム画像のURL"
        callback_url = "コールバックURL"
        finish_url = "購入完了URL"
        item_message = "メッセージ(GREEのみ) default=''"
        item_quantity = 1
        is_test = False

        cls = self._getTarget()
        res = cls.request_payment()
        #res = cls.request_payment(item_id, item_name, item_point,
        #item_description, item_image_url, callback_url, 
        #finish_url, item_message, item_quantity, is_test)
        eq_(None, res)

