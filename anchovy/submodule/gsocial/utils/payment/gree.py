# -*- coding: utf-8 -*-
from types import IntType
from django.utils import simplejson
from django.template import Context
from gsocial.models import PaymentInfo
from gsocial.log import Log
from django.conf import settings

from mobilejp.middleware.mobile import get_current_device

from gsocial.utils.payment.base import PaymentBase

class PaymentGree(PaymentBase):
    """
    Gree Payment API Class
    """

    def _api_request(self, userid, data):
        """
            paymentAPIへアクセスする

            This method will access to paymentAPI.
        """
        secure = True

        # iOSアプリの場合、LocalPayment APIを使う
        # If using iOS application,use LocalPayment API.
        app_user_agent = self.request.session.get('app_user_agent', None)
        is_webview = self.request.session.get('is_webview', None)
        if is_webview and app_user_agent == "iOS":
            # iOS only
            path = "/api/rest/local/payment/@me/@self/@app"
        else:
            # Andriod & WepApp
            path = "/api/rest/payment/@me/@self/@app"

        header = {'Content-Type': 'application/json; charset=utf8'}
        res = self.container.oauth_request('POST', userid, path,
                                 data=data, headers=header, url_tail='',
                                 body_hash=True, secure=secure)
        return res


    def _create_callback_url(self, callback_path = None):
        """
            callback_url生成

            Creates callback_url.
        """
        if self.request.is_smartphone:
            session_key = settings.SESSION_URL_KEY_NAME
            domain = settings.SITE_DOMAIN_SP
            session_id = self.request.session_id
            callback_url = 'http://%s%s?%s=%s' % (domain, callback_path,
                                                    session_key, session_id)
        else:
            domain = settings.SITE_DOMAIN_FP
            callback_url = 'http://%s%s' % (domain, callback_path)
        print callback_path
        return callback_url

    def _create_finish_url(self, finish_path = None):
        """
            finish_url生成

            Creates finish_url.
        """
        if self.request.is_smartphone:
            session_key = settings.SESSION_URL_KEY_NAME
            domain = settings.SITE_DOMAIN_SP
            session_id = self.request.session_id
            finish_url = 'http://%s%s?%s=%s' % (domain, finish_path,
                                                    session_key, session_id)
        else:
            domain = settings.SITE_DOMAIN_FP
            finish_url = 'http://%s%s' % (domain, finish_path)
        print finish_url
        return finish_url

    def _create_paydata(cls, item_id, item_name, item_point, item_description,
                        item_image_url, callback_url, finish_url,
                        item_message='', item_quantity=1, is_test=False, platform=None):
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
        platform: ios webview版の場合、"ios"。それじゃない場合（ディフォルト）、None

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
        platform: "ios" if iOS webview app, else None. default=None


        """
        #テンプレートは、payment/templates/payment_info.xml
        #templates is at payment/templates/payment_info.xml
        t = cls.container.payment_template()

        c = Context({ 'item_id': item_id,
                      'item_name': item_name,
                      'item_point': item_point,
                      'item_quantity': item_quantity,
                      'item_description': item_description,
                      'item_image_url': item_image_url,
                      'item_message': item_message,
                      'callback_url': callback_url,
                      'finish_url': finish_url,
                      'is_test': is_test,
                      'platform': platform })
        rendered = t.render(c)
        return rendered

    def request_payment(self, osuser_id, item_id, item_name, item_point,
                        item_description, item_image_url, callback_path,
                        finish_path, item_message='', item_quantity=1,
                        is_test=False):
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

        if not isinstance(item_id, IntType):
            # item_idはintでなければならない
            #item_id has to be in int
            raise

        callback_url = self._create_callback_url(callback_path)
        finish_url = self._create_finish_url(finish_path)

        app_user_agent = self.request.session.get('app_user_agent', None)
        platform = "ios" if app_user_agent is not None and app_user_agent == "iOS" else None

        paydata = self._create_paydata(item_id, item_name, item_point,
                                       item_description, item_image_url,
                                       callback_url, finish_url, item_message,
                                       item_quantity, is_test, platform)

        recv_data = self._api_request(osuser_id, paydata)
        Log.debug(recv_data)

        if recv_data is None:
            # 課金データ作成に失敗した場合
            # if you failed to make payment data
            Log.warn('Payment Data: osuser_id:%s, item_id:%s, item_name:%s, item_point:%s, item_description:%s, item_image_url:%s, callback_url:%s, finish_url:%s' % (osuser_id, item_id, item_name, item_point, item_description, item_image_url, callback_url, finish_url))
            raise

        json = simplejson.loads(recv_data)
        point_code = json['entry'][0]['paymentId']
        point_date = json['entry'][0]['orderedTime']
        point_url = json['entry'][0]['transactionUrl']

        app_user_agent = self.request.session.get('app_user_agent', None)


        # 決済情報を保存
        # saves payment information
        PaymentInfo.objects.create(
            point_code = point_code,
            item_id = item_id,
            osuser_id = osuser_id,
            point = item_point,
            quantity = item_quantity,
            send_data = paydata,
            point_date = point_date,
            point_url = point_url,
            recv_data = recv_data,
            device = self.device_type(),
            )
        return point_url

    def device_type(self):
        """
        Device Type:
            WebView: iOS: 4
            WebView: Android: 3
            WebApp : Smartphone: 2
            WebApp : Featurephone: 1
        """
        device_obj = get_current_device()

        if device_obj.is_webview:
            if device_obj.is_ios:
                device_type = 4
            elif device_obj.is_android:
                device_type = 3
        elif device_obj.is_smartphone:
            device_type = 2
        elif device_obj.is_featurephone:
            device_type = 1

        return device_type


    def callback(self):
        """
        PaymentCallback処理
        :return:
            True： 購入成功
            False： 購入キャンセル

         PaymentCallback processing
         :return:
            True: success of payment processing
            False: payment has been canceled
        """
        Log.debug("callback-------------")
        point_code =  self.request.REQUEST.get('paymentId', None)

        payment_obj = PaymentInfo.get_by_point_code(point_code)
        res = self.is_success()
        if res:
            payment_obj.save_as_succeeded()
        else:
            payment_obj.save_as_canceled()

        Log.debug("callback-------------")
        return res

    def is_success(self):
        """
        購入ステータスをチェック
        :return:
            True: 購入成功
            False: 購入キャンセル
        1回のビューで何度も呼ばれるようなら、結果をメモリに持ちたい

        check the status of payment
        :return:
            True: success of payment processing
            False: payment has been canceled
        If a view function needs to check is_success() in multiple places, call it once and store the result.
        """
        point_code =  self.request.REQUEST.get('paymentId', None)
        status =  self.request.REQUEST.get('status', None)
        if status is None:
            raise Exception('Payment (%s) status is None' % point_code)
        return int(status) == int(self.container.payment_success_status)

    def finish(self):
        """
        finish処理
        返り値:
            True： 購入
            False ： キャンセル

        finish processing
        return value:
            True: bought
            False: cancel

        """
        point_code =  self.request.REQUEST.get('paymentId', None)

        if point_code is not None:
            payment_obj = PaymentInfo.get_by_point_code(point_code)
            return payment_obj.is_succeeded()
