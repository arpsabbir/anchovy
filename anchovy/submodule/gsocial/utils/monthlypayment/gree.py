# -*- coding: utf-8 -*-
"""
MonthlyPayment
"""
from django.utils import simplejson
from django.template import loader, Context
from gsocial.set_container import Container

from django.conf import settings

from base import MonthlypaymentBase

class MonthlypaymentGree(MonthlypaymentBase):
    u"""
    Monthly Payment API Greeクラス
    Monthly Payment API Gree Class
    """

    def _api_path(self, method, os_user_id, transaction_id = None):
        """
        apiリスエスト用のpath生成
        
        Create paths for api request
        """
        if method == 'POST':
            path  = "/api/rest/subscription/%s/@self/@app" % os_user_id
        elif method == 'GET':
            path  = "/api/rest/subscription/%s/@self/@app/%s" % (os_user_id,
                                                                 transaction_id)
        return path


    def _api_request(self, method, os_user_id, transaction_id = None):
        """
        apiにリスエスト送信
        返り値
          正常時: リスエストのレスポンス
          異常時: None
          
        Request to the api.
        return value
           Usually: Request response
           If problems:None  
        """
        path = self._api_path(method, os_user_id, transaction_id)
        Log.debug("MonthlypaymentGree:_api_request")
        Log.debug(path)
        header = {'Content-Type': 'application/json; cahrset=utf8'}

        response = None

        try:
            if method == ['POST']:
                response = self.container.oauth_request(
                            method,
                            os_user_id,
                            path,
                            data = data,
                            headers = header,
                            url_tail='',
                            body_hash=True
                            )
            else:
                if transaction_id != None:
                    response = self.container.oauth_request(method,
                                                            os_user_id, path)
        except TypeError:
            Log.warn('Inspection: %s: response type error. userid:%s' %
                         (method, user_id))

        return response

    def _create_template(self):
        """
        リクエストに用いるtemplate生成
        Create template for request
        """
        t = cls.container.monthly_payment_template

        c = Context({ 'serviceid': servicdid,
                      'provider': provider,
                      'image_url': image_url,
                      'callback_url': callback_url,
                      'finish_url': finish_url,
                    })
        rendered = t.render(c)
        return rendered

