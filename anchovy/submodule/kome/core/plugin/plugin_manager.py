# coding: utf-8

_dic = { }

def _get_package(mod):
    """
    パッケージ名を取得する
    
    >>> _get_package('aaa.bbb.ccc.plugin_manager')
    aaa.bbb.ccc
    """
    return '.'.join(mod.split('.')[:-1])

def get(name):
    __import__(_get_package(__name__) + '.' + name)
    return _dic[name]

def register(name, cls):
    _dic[name] = cls
