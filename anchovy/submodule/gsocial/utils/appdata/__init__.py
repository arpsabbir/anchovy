# -*- coding: utf-8 -*-
"""
APPDATA API
"""

from gsocial.set_container import Container
from gsocial.setting import *

class MetaAppData(type):
    '''
    コンテナー対応クラスをベースにする
    '''
    def __new__(meta, name, bases, attrs):
#        if Container().name == GREE:


        return type.__new__(meta, name, bases, attrs)

class AppData(object):
    '''
    Message APIを使う（抽象）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaAppData
