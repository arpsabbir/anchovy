# -*- coding: utf-8 -*-
"""
#------------------------------------
#People API
#------------------------------------
"""
from gsocial.utils.people.gree import PeopleGree
from gsocial.utils.people.mixi import PeopleMixi
from gsocial.utils.people.mobage import PeopleMobage

class MetaPeople(type):
    '''
    コンテナー対応クラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
        from gsocial.setting import GREE, MOBAGE, MIXI
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (PeopleGree,)
        elif Container().name == MOBAGE:
            bases = (PeopleMobage,)
        elif Container().name == MIXI:
            bases = (PeopleMixi,)

        return type.__new__(meta, name, bases, attrs)

class People(object):
    '''
    Activity APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaPeople

