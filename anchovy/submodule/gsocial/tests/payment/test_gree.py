# -*- coding: utf-8 -*-

import unittest
import requests
import mock
from mock import patch
from nose.tools import *

class PaymentGreeTests(unittest.TestCase):

    def _getTarget(self):
        from gsocial.utils.payment.gree import PaymentGree
        res =  requests.Response()
        return PaymentGree(res)

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

    def test_get_mobilepayment(self):
        cls = self._getTarget()
        cls.container.oauth_request = mock.Mock(name = "method")
        cls.container.oauth_request.return_value = True
        # eq_(True, cls.get_mobilepaydata(1, {}))
        # utils.payment.gree に get_mobilepaydata が実装されていないのでエラーになる?

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
        res = cls._create_paydata(item_id, item_name, item_point, item_description, item_image_url, callback_url, finish_url, item_message, item_quantity, is_test)
         

    def test_request_payment(self):
        osuser_id = 'test0001'
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
        # OAuth認証をパスしないとテストできない
        #res = cls.request_payment(item_id, item_name, item_point, item_description, item_image_url, callback_url, finish_url, item_message, item_quantity, is_test)


#    def test_callback(self):
#    　　 予め request_payment() を動かして、レコードを作っていないとテストできない
#
#        from gsocial.utils.payment.gree import PaymentGree
#        from gsocial.set_container import containerdata
#        res =  requests.Response()
#        res.REQUEST = {
#            'paymentId': 'test1',
#            'status': containerdata.get('payment_success_status'),
#            }
#        cls = PaymentGree(res)
#        result = cls.callback()
#        eq_(True, result)
#
