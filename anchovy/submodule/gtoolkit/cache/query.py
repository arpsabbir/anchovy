# -*- coding: utf-8 -*-
"""
Paginator に QuerySet を渡すとキャッシュが効かない.
Paginator にキャッシュから取り出したリストを渡すとメモリ効率が悪い.

そこで, QuerySet のリストのスライスアクセスの結果をキャッシュする.
ついでに, get() もキャッシュしてしまう.

Memcached のコマンド(add, gets, cas)に依存しているため,
Django Settings の CACHES に
django.core.cache.backends.memcached.MemcachedCache を指定しなければ,
通常の QuerySet として振る舞う.

--------
事前準備
--------

Scope Chanin 用の QuerySet を作る際,
django.db.models.query.QuerySet の代わりに, CachedQuerySet を使用する.

.. code-block:: python

    from gtoolkit.cache.query import CachedQuerySet

    class EggQuerySet(CachedQuerySet):
        pass


次に, Manager の get_query_set が CachedQuerySet のインスタンスを返すようにする.

.. code-block:: python

    from django.db import models

    class EggManager(models.Manager):
        def get_query_set(self):
            return EggQuerySet(self.model)
        

最後に, モデルの objects に Manager を設定する.

.. code-block:: python

    class Egg(models.Model):
        objects = EggManager()


--------
使用方法
--------

キャッシュされた QuerySet を取得するには, manage_cache() を使用する.

.. code-block:: python

    def get_sandwiches():
        return Egg.objects.filter(spam=1).manage_cache('sand').filter(ham='good')


manage_cache() には, キャッシュ管理キーとして使用する文字列を引数として渡す.

キャッシュ管理キーには, 接頭辞としてパッケージ名とモデル名が自動付与される.
省略した場合, パッケージ名とモデル名がキャッシュ管理キーとして使用される.

キャッシュ管理キーには, 複数の SQL Query が自動で紐づくため,
発行される SQL Query 毎にキャッシュ管理キーを分割する必要はない.

ただし, キャッシュの削除は, キャッシュ管理キー単位で行うため,
削除する単位で分割する必要がある.

キャッシュ削除の方法は後述する.

manage_cache() は, Scope Chanin のどの位置で使用しても良いが,
Manager に存在しないため, filter() を付加したくない場合は,
Manager の get_query_set() で QuerySet を取り出してから,
manage_cache() を使用する.

キャッシュされるアクセス方法は次の通り.

.. code-block:: python

    def success_test():
        sandwiches = get_sandwiches()
        print len(sandwiches)
        print sandwiches.count()
        print sandwiches[0]
        print sandwiches[:1]
        print sandwiches[10:100]
        print sandwiches[10:100:2]

        # list(sandwiches) の代わりに使用できる
        print sandwiches[:]

        # get() もキャッシュされる
        print sandwiches.get(id=1)


キャッシュされた値は, delete_cache() で削除できる.

.. code-block:: python

    def create_or_update_or_delete_egg():
        # do something ... (Egg のレコード操作)
        Egg.objects.get_query_set().manage_cache('sand').delete_cache()


manage_cache() で指定したキャッシュ管理キーには,
複数の SQL Query が紐づいており, delete_cache() を実行すると, 
紐づけられているキャッシュ全てが削除される.

CachedQuerySet の delete() と update() は,
内部で delete_cache() を実行するため,
明示的に delete_cache() を実行する必要はない.

.. code-block:: python

    def update_test():
        Egg.objects.filter(spam=1).manage_cache('sand').update(ham='like')

    def delete_test():
        Egg.objects.filter(spam=1).manage_cache('sand').delete()
"""
import logging
from hashlib import sha256

from django.core.cache import cache
from django.db.models.query import QuerySet

_logger = logging.getLogger('cached_query')

class _ManageCacheMixin(object):
    _manage_cache_key = None
    _try_cas_count = 100

    def manage_cache(self, key=''):
        """
        キャッシュ管理を開始する.

        :param str key: キャッシュ管理キー. delete_cache の引数にも使用する.
        """
        for attr in ['add', 'gets', 'cas']:
            if not hasattr(cache._cache, attr):
                return self

        self._manage_cache_key = self._make_manage_cache_key(key)
        cache._cache.add(self._manage_cache_key, [])

        return self

    def _make_manage_cache_key(self, key):
        return "CachedQuerySet:{}.{}:{}".format(self.model.__module__,
                                                self.model.__name__,
                                                key)

    @property
    def _can_manage_cache(self):
        return self._manage_cache_key is not None

    def _store_cache_key(self, cache_key):
        if not self._can_manage_cache:
            return True

        for n in xrange(self._try_cas_count):
            keys = cache._cache.gets(self._manage_cache_key)
            if keys is None: # ElastiCache に変更してから None の可能性あり
                return False

            if cache_key in keys:
                return True

            keys.append(cache_key)
            if cache._cache.cas(self._manage_cache_key, keys):
                return True

        return False

    def _cache_keys_for_delete(self):
        for n in xrange(self._try_cas_count):
            keys = cache._cache.gets(self._manage_cache_key)
            if cache._cache.cas(self._manage_cache_key, []):
                return keys
        return []


class CachedQuerySet(_ManageCacheMixin, QuerySet):
    def __getitem__(self, k):
        def f():
            result = super(CachedQuerySet, self).__getitem__(k)
            if isinstance(k, slice):
                return list(result)
            else:
                return result
        return self._eval_on_cached(k, f)

    def __len__(self):
        def f():
            return super(CachedQuerySet, self).__len__()
        return self._eval_on_cached('length', f)

    def __iter__(self):
        def f():
            # iter の意味ないけど仕方ない
            return [obj for obj in super(CachedQuerySet, self).__iter__()]
        objs = self._eval_on_cached('iter', f)
        return iter(objs)

    def count(self):
        return self.__len__()

    def get(self, *args, **kwargs):
        clone = self.filter(*args, **kwargs)
        def f():
            return super(CachedQuerySet, clone).get()
        return clone._eval_on_cached('get', f)

    def filter(self, *args, **kwargs):
        clone = super(CachedQuerySet, self).filter(*args, **kwargs)
        clone._manage_cache_key = self._manage_cache_key
        return clone

    def _eval_on_cached(self, k, f):
        if not self._can_manage_cache:
            return f()

        if self.query.select_for_update:
            _logger.debug('FOR UPDATE(%s): %s %s',
                          self._manage_cache_key, self.query, k)
            return f()

        cache_key = self._cache_key(k)

        result = cache.get(cache_key)
        if result:
            _logger.debug('HIT(%s): %s %s',
                          self._manage_cache_key, self.query, k)
            return result

        if not self._store_cache_key(cache_key):
            _logger.debug('CAS ERROR(%s): %s %s',
                          self._manage_cache_key, self.query, k)
            return f()

        _logger.debug('THROUGH(%s): %s %s',
                      self._manage_cache_key, self.query, k)
        result = f()
        cache.set(cache_key, result)
        return result

    def _cache_key(self, k):
        return sha256(str(self.query) + str(k)).hexdigest()

    def delete_cache(self):
        if not self._can_manage_cache:
            return

        _logger.debug('DELETE(%s)', self._manage_cache_key)
        for cache_key in self._cache_keys_for_delete():
            cache.delete(cache_key)

    def delete(self, *args, **kwargs):
        self.delete_cache()
        return super(CachedQuerySet, self).delete(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.delete_cache()
        return super(CachedQuerySet, self).update(*args, **kwargs)
