# -*- coding: utf-8 -*-
"""
#------------------------------------
#Request API 実装中
#------------------------------------
"""
from gsocial.utils.request.gree import RequestGree
class MetaRequest(type):
    '''
    コンテナー対応クラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
        from gsocial.setting import GREE,MOBAGE,MIXI
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (RequestGree,)
        return type.__new__(meta, name, bases, attrs)

class Request(object):
    '''
    Request APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaRequest

