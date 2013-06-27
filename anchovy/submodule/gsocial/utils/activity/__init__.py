# -*- coding: utf-8 -*-
"""
API呼び出し

Call the API
"""

#------------------------------------
#ACTIVITY API
#------------------------------------
from gsocial.utils.activity.gree import ActivityGree
from gsocial.utils.activity.mixi import ActivityMixi
from gsocial.utils.activity.mobage import ActivityMobage

class MetaActivity(type):

    '''
    コンテナー対応クラスをベースにする
    
    Make class from information in container(gree,mixi,mobage...).
    '''
    def __new__(meta, name, bases, attrs):
        from gsocial.setting import GREE, MOBAGE, MIXI
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (ActivityGree,)
        elif Container().name == MOBAGE:
            bases = (ActivityMobage,)
        elif Container().name == MIXI:
            bases = (ActivityMixi,)

        return type.__new__(meta, name, bases, attrs)

class Activity(object):
    '''
    Activity APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    
    Use Activity Api.
    Each platforms have to implement this.
    '''
    __metaclass__ = MetaActivity


