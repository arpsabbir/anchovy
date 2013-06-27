# -*- coding: utf-8 -*-
"""
#------------------------------------
#INSPECTION API
#------------------------------------
"""
from gsocial.utils.inspection.gree import InspectionGree

class MetaInspection(type):
    """
    Inspectionのベース切り替えメタクラス
    """
    def __new__(mcs, name, bases, attrs):
        from gsocial.setting import GREE, MOBAGE, MIXI
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (InspectionGree,)
        return type.__new__(mcs, name, bases, attrs)

class Inspection(object):
    '''
    Inspection APIを使う（実装）
    プラットフォーム別の動作はこれを実体化させること
    '''
    __metaclass__ = MetaInspection

