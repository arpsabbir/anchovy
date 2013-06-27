# -*- coding: utf-8 -*-
"""
#------------------------------------
#BlackList API
#------------------------------------
"""
from gsocial.utils.blacklist.gree import BlacklistGree
from gsocial.utils.blacklist.mixi import BlacklistMixi
from gsocial.utils.blacklist.mobage import BlacklistMobage

class MetaBlacklist(type):
    '''
    コンテナー対応クラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
        from gsocial.setting import GREE, MOBAGE, MIXI
        from gsocial.set_container import Container

        if Container().name == GREE:
            bases = (BlacklistGree,)
        elif Container().name == MOBAGE:
            bases = (PeopleMobage,)
        elif Container().name == MIXI:
            bases = (PeopleMixi,)

        return type.__new__(meta, name, bases, attrs)

class Blacklist(object):
    '''
    Blacklist APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaBlacklist

