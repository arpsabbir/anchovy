# -*- coding: utf-8 -*-
"""
payment base class
"""
#from types import IntType
#from django.utils import simplejson
#from django.template import loader, Context
from gsocial.models import PaymentInfo
from gsocial.set_container import Container

#from django.conf import settings

class PaymentBase(object):
    """
    Payment API の基底クラス
    Base class of Payment API
    """
    def __init__(self, request):
        # OpenSocialのContainerを作成する
        self.request = request
        self.container = Container(request)

    def get_mobilepaydata(self, userid, data):
        """
            paymentAPIへアクセスする
            
            Access to paymentAPI
        """
        return None

    def callback_url(self, callback_path):
        """
        return call back url path
        """
        pass

    def finish_url(self, finish_path):
        """
        return finish url path
        """
        pass


    def _create_paydata(self):
        """
        課金情報を生成する
        item_id: アイテムID
        item_name: アイテム名
        item_point: アイテム価格
        item_description： アイテム説明文
        item_image_url: アイテム画像のURL
        callback_url: コールバックURL
        finish_url: 購入完了URL
        item_message: メッセージ(GREEのみ) default='' 
        item_quantity: アイテムの個数 default=1
        is_test: テストフラグ(mixiのみ有効) default=False
        
        
        Creates payment information.
        item_id: the id of the item
        item_name: the name of the item
        item_point: the price of the item
        item_description： the description of the item
        item_image_url: the url of the image of the item
        callback_url: the url of the callback
        finish_url: the url if the payment finished successfully. 
        item_message: Messages(only for Gree). default=''
        item_quantity: the number of the item. default=1
        is_test: the test flag(only for mixi) default=False
        """

        return None


    def request_payment(self):
        """
        課金処理開始
        Arguments
        request: Django requestインスタンス
        osuser_id: OpensocialUserのID
        item_id: アイテムID アイテムを識別するためのID
        item_name: アイテム名
        item_point: アイテム価格
        item_description： アイテム説明文
        item_image_url: アイテム画像のURL
        callback_url: コールバックURL
        finish_url: 購入完了URL
        item_message: メッセージ(GREEのみ) default='' 
        item_quantity: アイテムの個数 default=1
        is_test: テストフラグ(mixiのみ有効) default=False

        Return
        payment_url: 購入画面のURL。 次に進むべきページのURL
        
       Start processing the payment.
         Arguments
        request: Django request instance
        osuser_id: ID of OpensocialUser
        item_id: Item ID 
        item_name: Item Name
        item_point: Item price
        item_description： Item description
        item_image_url: Url of item image
        callback_url: callback url
        finish_url: purchase finish url
        item_message: message(only for GREE) default='' 
        item_quantity: item number default=1
        is_test: test flag(only for mixi) default=False

        Return
        payment_url: payment url.the url which will be redirected.
        

        """

        return None

