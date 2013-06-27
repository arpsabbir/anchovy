# -*- coding: utf-8 -*-
"""
gtoolkit 依存は避けたいが, ここで gtoolkit の memoize を import する.
後で, horizontalpartitioning のモジュール整理を行う.
"""
from django.db.models.query import QuerySet

try:
    from gtoolkit.cache.memoize import (MemoizedQuerySet,
                                        clear_request_memoize_cache_query)
except ImportError:
    class MemoizedQuerySet(QuerySet):
        pass


    def clear_request_memoize_cache_query():
        pass
