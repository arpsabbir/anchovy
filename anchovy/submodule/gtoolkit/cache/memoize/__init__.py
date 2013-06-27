# -*- coding: utf-8 -*-
"""
リクエスト毎に関数をメモ化する

使用方法は次の通り.

.. code-block:: python

    from gtoolkit.cache.memoize import request_memoize

    @memoize(1)
    def ham(egg):
        return egg


引数は, キャッシュキーに使用する引数の数.
kwargs を使用する関数のメモ化は行えない.

MemoizePerRequestMiddleware.process_request
が実行される前に関数を実行された場合,
キャッシュが利用せずにラップした関数を通常実行する.

クラスメソッドのメモ化に使用する場合は, 次の通り.

.. code-block:: python

    class Spam(object):
        @classmethod
        @memoize(2)
        def ham(cls, egg):
            return egg
"""
from gtoolkit.cache.memoize.function import (
    request_memoize,
    clear_cache as clear_request_memoize_cache,)

from gtoolkit.cache.memoize.query import (
    MemoizedQuerySet,
    clear_cache as clear_request_memoize_cache_query,)
