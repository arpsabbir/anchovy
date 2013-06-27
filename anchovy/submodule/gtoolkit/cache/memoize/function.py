# -*- coding: utf-8 -*-
import logging
from functools import wraps

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
_logger = logging.getLogger('memoize')

def _generate_cache_key(func, args, num_args):
    """
    キャッシュのキーを返す.
    """
    keys = [repr(v) for v in args[:num_args]]
    keys.insert(0, func.__module__ + '.' + func.__name__)
    return ':'.join(keys)

def request_memoize(num_args):
    """
    リクエスト単位でメモ化するデコレータ
    """
    logging.getLogger('ggacha')

    def deco(func):
        @wraps(func)
        def wrapper(*args):
            cache = getattr(_thread_locals, 'cache', None)
            if cache is None:
                return func(*args)

            key = _generate_cache_key(func, args, num_args)
            if key in cache:
                _logger.debug('HIT: %s', key)
                return cache[key]

            _logger.debug('THROUGH: %s', key)
            result = func(*args)
            cache[key] = result
            return result
        return wrapper
    return deco

def clear_cache():
    """
    キャッシュを初期化する
    """
    _logger.debug('clear cache')
    _thread_locals.cache = {}
