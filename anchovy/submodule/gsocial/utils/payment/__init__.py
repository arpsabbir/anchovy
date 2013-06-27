# -*- coding: utf-8 -*-
"""
#------------------------------------
#PAYMENT API
#------------------------------------
"""

from gsocial.utils.payment.gree import PaymentGree

class MetaPayment(type):
    '''
    適切なクラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
        from gsocial.setting import GREE,MOBAGE,MIXI
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (PaymentGree,)
        return type.__new__(meta, name, bases, attrs)

class Payment(object):
    '''
    PaymentAPIクラス
    '''
    __metaclass__ = MetaPayment

