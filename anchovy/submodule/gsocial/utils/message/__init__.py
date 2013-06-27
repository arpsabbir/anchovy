# -*- coding: utf-8 -*-
"""
#------------------------------------
#MESSAGE API
#------------------------------------
"""
from gsocial.utils.message.gree import MessageGree

class MetaMessage(type):
    '''
    コンテナー対応クラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
        from gsocial.setting import GREE
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (MessageGree,)
        return type.__new__(meta, name, bases, attrs)

class Message(object):
    '''
    Message APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaMessage

