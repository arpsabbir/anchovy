# -*- coding: utf-8 -*-
"""
旧 gu3.KVS の generic like class.
gkvs に依存している. 利用方法は次の通り.

初めに Factory Class の定義を行う.

.. code-block:: python

    from gtoolkit.redis.generic import RedisHash

    class EggHash(RedisHash):
        name = 'django.conf.settings.REDIS_DATABASES のキー名'
        key = 'Redis で使用するキー名'
        expire = 60 # 有効期限(秒)


name
    django.conf.settings.REDIS_DATABASES のキー名.
    省略すると 'default' を使用する.

expire
    有効期限(秒).
    後述の with/Decorator で使用する際,
    gkvs の store() に引数として expire を渡す.


RedisHash 以外に, RedisString, RedisArray が用意されている.
定義した Factory Class の使用方法は次の通り.

>>> h = EggHash.create()
>>> h['spam'] = 'ham'
>>> h.store()

create() で gkvs.Hash の Object を取得できる.
create() では, Redis で使用するキー名を create(key) の形式で指定できる.
実際に Redis で使用するキー名は, "gkvs:generic:Hash:EggHash" + key となる.

その他の動作は, gkvs.Hash 本体のドキュメント参照の事.

ただし, この使い方では, EggHash.expire は使用されない.

gkvs の Factory ではなくオブジェクトとして使うと,
with や Decorator として使用できる.

>>> with EggHash() as h:
>>>     h['spam'] = 'ham'
>>>     h['ham'] = 'egg'

>>> @EggHash()
>>> def spam(h):
>>>     h['spam'] = 'ham'
>>>     h['ham'] = 'egg'

ブロックを抜けた時点で, store() が自動実行される.
raise すると, gkvs の store() が実行されないため, 修正が反映されない.

また, with/Decorator を使用すると,
Mutex Lock を行うため, Race Condition は発生しない.

もし, Mutex Lock を行わないのであれば, use_mutex フラグに False を設定する.

.. code-block:: python

    class EggHash(RedisHash):
        use_mutex = False


値に 100 文字以上, 要素に 100 要素以上を設定する場合, 下記のようにする.

gkvs の仕様で, validate を指定する場合は, max_xxx を省略できないので注意する事.
この仕様は, 後で gkvs を修正する事で対応する.

.. code-block:: python

    class EggHash(RedisHash):
        validate = {
            'max_key': 1024,   # キーの最大長
            'max_value': 1024, # 値の最大長
            'max_list': 1024,  # 要素の最大数
        }
"""
import logging
from functools import wraps

from gredis import get_pool
import gmutex
from gkvs.redis import String, Array, Hash
from gkvs.util.validator import Validator

_logger = logging.getLogger('redis.generic')

class _Base(object):
    _prefix = 'gkvs:generic'
    name = 'default'
    use_mutex = True
    expire = None
    validate = None

    @classmethod
    def _kind(cls):
        raise NotImplementedError

    @classmethod
    def create(cls, key=None):
        # gkvs は, validate=None を許さない. 後で gkvs を修正する.
        if cls.validate:
            kwargs = {'validator': Validator(config=cls.validate)}
        else:
            kwargs = {}
        return cls._kind().prepare(cls._make_key(key),
                                   connection_pool=get_pool(cls.name),
                                   **kwargs)

    @classmethod
    def _make_key(cls, key):
        keys = [cls._prefix, cls._kind().__name__, cls.__name__]
        if key:
            keys.append(key)
        return ':'.join(keys)

    def __init__(self, key=None):
        self._key = key

        if self.use_mutex:
            self._mutex = gmutex.get(self._make_key(key))

    def __enter__(self):
        if self.use_mutex:
            self._mutex.lock()

        self._gkvs = self.create(self._key)
        _logger.debug('__enter__(%s): %s',
                      self._make_key(self._key), repr(self._gkvs))
        return self._gkvs

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            if self.use_mutex:
                self._mutex.unlock()
            return False

        try:
            _logger.debug('__exit__:start:(%s): %s',
                          self._make_key(self._key), repr(self._gkvs))
            self._gkvs.store(expire=self.expire)
            _logger.debug('__exit__:finish:(%s): %s',
                          self._make_key(self._key), repr(self._gkvs))
        finally:
            if self.use_mutex:
                self._mutex.unlock()
        return True

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self as obj:
                return func(obj, *args, **kwargs)
        return inner


class RedisString(_Base):
    @classmethod
    def _kind(cls):
        return String 


class RedisArray(_Base):
    @classmethod
    def _kind(cls):
        return Array


class RedisHash(_Base):
    @classmethod
    def _kind(cls):
        return Hash
