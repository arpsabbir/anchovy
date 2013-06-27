# -*- coding: utf-8 -*-
"""
Avator
"""

from gsocial.setting import *
from gsocial.set_container import Container

class MetaMessage(type):
    '''
    適切なクラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
        pass

class Message(object):
    '''
    Message APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaMessage
