# -*- coding: utf-8 -*-
"""
QuerySet をリクエスト毎にメモ化する
"""
import logging
from hashlib import sha256

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

from django.db.models.query import QuerySet

_thread_locals = local()
_logger = logging.getLogger('memoize_query')

class MemoizedQuerySetMixin(object):
    def __getitem__(self, k):
        def f():
            result = super(MemoizedQuerySetMixin, self).__getitem__(k)
            if isinstance(k, slice):
                return list(result)
            else:
                return result
        return self._eval_on_cached(k, f)

    def __len__(self):
        def f():
            return super(MemoizedQuerySetMixin, self).__len__()
        return self._eval_on_cached('length', f)

    def __iter__(self):
        def f():
            # iter の意味ないけど仕方ない
            return [obj for obj in super(MemoizedQuerySetMixin, self).__iter__()]
        objs = self._eval_on_cached('iter', f)
        return iter(objs)

    def count(self):
        return self.__len__()

    def get(self, *args, **kwargs):
        clone = self.filter(*args, **kwargs)
        def f():
            return super(MemoizedQuerySetMixin, clone).get()
        return clone._eval_on_cached('get', f)

    def _eval_on_cached(self, k, f):
        if getattr(self, '_disable_memoize', False):
            _logger.debug('disabled: %s %s', self.query, k)
            return f()

        cache = getattr(_thread_locals, 'query_cache', None)
        if cache is None:
            return f()

        if self.query.select_for_update:
            _logger.debug('FOR UPDATE: %s %s', self.query, k)
            return f()

        cache_key = self._cache_key(k)

        result = cache.get(cache_key)
        if result:
            _logger.debug('HIT: %s %s', self.query, k)
            return result

        _logger.debug('THROUGH: %s %s', self.query, k)
        result = f()
        cache[cache_key] = result
        return result

    def _cache_key(self, k):
        return sha256(str(self.query) + str(k)).hexdigest()

    def delete_cache(self):
        clear_cache()

    def delete(self, *args, **kwargs):
        self.delete_cache()
        return super(MemoizedQuerySetMixin, self).delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.delete_cache()
        return super(MemoizedQuerySetMixin, self).update(*args, **kwargs)

    def disable_memoize(self):
        self._disable_memoize = True
        return self


class MemoizedQuerySet(MemoizedQuerySetMixin, QuerySet):
    pass


def clear_cache():
    """
    キャッシュを初期化する
    """
    _logger.debug('clear query cache')
    _thread_locals.query_cache = {}
