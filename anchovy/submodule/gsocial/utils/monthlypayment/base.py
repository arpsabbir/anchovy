# -*- coding: utf-8 -*-
"""
MonthlyPayment
"""
#from django.utils import simplejson
#from django.template import loader, Context
from gsocial.models import PaymentInfo
from gsocial.set_container import Container

from django.conf import settings

class MonthlypaymentBase(object):
    """
    Monthly Payment API の基底クラス
    A base class for Monthly Payment API
    """
    def __init__(self, request):
        # OpenSocialのContainerを作成する
        self.request = request
        self.container = Container(request)

    def _api_request(self):
        """
        apiへのrequest処理
        
        Processing request for api.
        """
        pass

