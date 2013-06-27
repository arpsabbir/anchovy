# -*- coding: utf-8 -*-

from django.conf import settings
from kvstypes import KVS_TYPES

DEFAULT_KVS_CLASS = 'TTObj'
KVS_TYPE_SETTINGS = 'KVS_DEFAULT_TYPE'

class KVSFactoryError(Exception):
    pass

def create_kvs_class(t=None):
    """
    KVSクラス生成
    """
    ##print str(t)
    if t is None:
        if hasattr(settings, KVS_TYPE_SETTINGS):
            t = getattr(settings, KVS_TYPE_SETTINGS)
        else:
            t = DEFAULT_KVS_CLASS

    try:
        cls = KVS_TYPES[t]
        return cls
    except KeyError:
        raise KVSFactoryError('Invalid KVS type(%s)' % str(t))

DEFAULT_KVS_ENGINE = 'Redis'
DEFAULT_KVS_TYPE = 'OBJ'
KVS_DEFAULT_ENGINE_SETTINGS = 'DEFAULT_KVS_ENGINE'
KVS_DEFAULT_TYPE_SETTINGS = 'DEFAULT_KVS_TYPE'

KVS_CLASS_MAP = {
    'TokyoTyrant': {
        'INT': 'TTInt',
        'STR': 'TTStr',
        'OBJ': 'TTObj',
        },
    'Redis': {
        'INT': 'RedisInt',
        'STR': 'RedisStr',
        'OBJ': 'RedisObj',
        }
}

class KVSClassNameError(Exception):
    pass

def get_kvs_class_name(type=None, engine=None):

    # 指定がなければデフォルトのエンジンを使う
    if engine is None:
        if hasattr(settings, KVS_DEFAULT_ENGINE_SETTINGS):
            engine = getattr(settings, KVS_DEFAULT_ENGINE_SETTINGS)
        else:
            engine = DEFAULT_KVS_ENGINE

    # 指定が無ければデフォルトの型を使う
    if type is None:
        if hasattr(settings, KVS_DEFAULT_TYPE_SETTINGS):
            type = getattr(settings, KVS_DEFAULT_TYPE_SETTINGS)
        else:
            type = DEFAULT_KVS_TYPE

    try:
        cls_name = KVS_CLASS_MAP[engine][type]
        return cls_name
    except KeyError:
        raise KVSClassNameError('Invalid KVS class name. engine[%s] type[%s]' % (str(engine), str(type)))
