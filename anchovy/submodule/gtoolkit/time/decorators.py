# -*- coding: utf-8 -*-

import time
import logging
from functools import wraps

try:
    from django.conf import settings
except ImportError:
    settings = object()


def debug_elapsed_time(func):
    """
    関数の実行時間を表示するデコレータ
    >>> import time
    >>> def func():
    ...    time.sleep(0.001)
    >>> func = debug_elapsed_time(func)
    >>> func() # doctest: +ELLIPSIS
    [func] end. ...ms
    >>> func.func_name
    'func'
    """
    @wraps(func)
    def decorate(*args, **kw):
        start_time = time.time()
        ret = func(*args, **kw)
        #print('[%s] start. args=%r, kw=%r' % (func.func_name, args, kw))
        delta = time.time() - start_time
        l = '[{}] end. {}ms'.format(func.func_name,int(delta*1000))
        if getattr(settings, 'DEBUG', False):
            print(l)
        logging.debug(l)
        return ret
    return decorate