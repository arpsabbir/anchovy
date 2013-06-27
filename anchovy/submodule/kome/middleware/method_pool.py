# coding: utf-8

import inspect

def _check_callable(cls, method, *args, **kwargs):
    if hasattr(inspect, 'getcallargs'):
        # for Python 2.7 or later.
        inspect.getcallargs(getattr(cls, method), cls, *args, **kwargs)
    else:
        # for Python 2.6 or earlier.
        if not hasattr(cls, method):
            raise AttributeError, 'This class has not attr: ' + method

class MethodPool(object):
    """
    メソッド呼び出しを溜めておくクラス

    call_methods() を呼び出すことで、溜めておいた処理を一気に呼び出すことができる。
    """
    def __init__(self, cls):
        self._cls = cls
        self._funcs = []

    def __getattr__(self, name):
        def proxy(*args, **kwargs):
            _check_callable(self._cls, name, *args, **kwargs)

            self._funcs.append(lambda self_: getattr(self._cls, name)(self_, *args, **kwargs))
        return proxy

    def call_methods(self, self_):
        funcs = self._funcs
        self._funcs = []
        return [f(self_) for f in funcs]

