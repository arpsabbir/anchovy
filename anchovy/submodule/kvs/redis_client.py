# -*- coding: utf-8 -*-

import threading
import functools

import redis

## グローバルパラメータ
connection_pooling=True # コネクションプールを行うか
connection_limit=1 # コネクションプールの際の1プロセスあたりの最大接続数
use_common_pooling=False # gtoolkit.redis を使うか

## Djangoの設定を反映
try:
    from django.conf import settings
    connection_pooling = getattr(settings, 'REDIS_CONNECTION_POOLING', True)
    connection_limit = getattr(settings, 'REDIS_CONNECTION_LIMIT', 1)
    use_common_pooling = getattr(settings,
                                 'USE_COMMON_REDIS_CONNECTION_POOLING',
                                 False)
except ImportError:
    pass

DEFAULT_PORT=6379
DEFAULT_DB=0

CONNECTION_POOL={}

SEMA_POOL=threading.BoundedSemaphore(value=connection_limit)

class ClientDoesNotDefinedError(Exception):
    pass

def get_client(name="default", setting=None):

    global connection_pooling
    global use_common_pooling

    if not setting:
        raise ClientDoesNotDefinedError('No setting')

    if name not in setting:
        raise ClientDoesNotDefinedError('Not defined setting (%r)' % name)

    if use_common_pooling:
        from gtoolkit.redis import get as redis_get
        return RedisClient(setting[name], client=redis_get(name))

    connection = None
    if connection_pooling:
        if name not in CONNECTION_POOL:
            CONNECTION_POOL[name] = get_connection(setting[name])
        connection = CONNECTION_POOL[name]

    return RedisClient(setting[name], connection=connection)


def get_connection(setting):
    s = setting
    opts = {
        'host' : s['HOST'],
        'port' : int(s.get('PORT', DEFAULT_PORT)),
        'db'   : s.get('DB', DEFAULT_DB),
    }
    return RedisConnection(**opts)

class RedisKVSError(Exception):
    pass


class RedisConnectionError(RedisKVSError):
    pass

class RedisConnection(object):
    def __init__(self, host='127.0.0.1', port=DEFAULT_PORT, db=DEFAULT_DB):
        global connection_limit

        self.host = host
        self.port = port
        self.db = db

        self.con = redis.ConnectionPool(max_connections=connection_limit,
                                        host=self.host,
                                        port=self.port,
                                        db=self.db,
                                        )

        if not self.con:
            raise RedisConnectionError

class RedisClient(object):

    class Error(RedisKVSError):
        pass

    class CannotGetRedisClient(RedisKVSError):
        pass

    def __init__(self, setting, connection=None, client=None):
        global use_common_pooling

        self.setting = setting

        if use_common_pooling and client is not None:
            self.client = client
        else:
            self.connection = connection if connection else get_connection(setting)
            self.client = redis.Redis(connection_pool=self.connection.con)

        if not self.client:
            raise self.CannotGetRedisClient

    def execute(self, f):
        global connection_pooling

        if connection_pooling:
            # プーリング制御を行う
            SEMA_POOL.acquire()
            try:
                v = f()
            finally:
                SEMA_POOL.release()
        else:
            v = f()

        return v

    def get(self, key, default=None):
        v = self.execute(functools.partial(self.client.get, key))
        if v is None:
            return default

        return v

    def set(self, key, value):
        self.execute(functools.partial(self.client.set, key, value))

    def delete(self, key):
        self.execute(functools.partial(self.client.delete, key))

    '''
    INTEGER
    '''
    def getint(self, key, default=None):
        v = self.get(key, default=default)
        if v == default:
            return v

        return int(v)

    def setint(self, key, value):
        if not isinstance(value, (int, long)):
            raise TypeError("int or long argument required")

        self.set(key, value)

    def addint(self, key, num):
        return self.execute(functools.partial(self.client.incr, key, num))

    '''
    LIST
    '''
    def push(self, key, value):
        self.execute(functools.partial(self.client.lpush, key, value))

    def append(self, key, value):
        self.execute(functools.partial(self.client.rpush, key, value))

    def range(self, key, start=0, end=-1):
        return self.execute(functools.partial(self.client.lrange, key, start, end))

    def len(self, key):
        return self.execute(functools.partial(self.client.llen, key))

    def index(self, key, idx):
        return self.execute(functools.partial(self.client.lindex, key, idx))

    def lset(self, key, idx, value):
        return self.execute(functools.partial(self.client.lset, key, idx, value))

    '''
    BITSET
    '''
    def setbit(self, key, offset, value):
        return self.execute(functools.partial(self.client.setbit, key, offset, value))

    def getbit(self, key, offset):
        return self.execute(functools.partial(self.client.getbit, key, offset))

    '''
    Hash
    '''
    def hdel(self, key, *fields):
        return self.execute(functools.partial(self.client.hdel, key, *fields))

    def hexists(self, key, field):
        return self.execute(functools.partial(self.client.hexists, key, field))

    def hget(self, key, field):
        return self.execute(functools.partial(self.client.hget, key, field))

    def hgetall(self, key):
        return self.execute(functools.partial(self.client.hgetall, key))

    def hincrby(self, key, field, increment=1):
        return self.execute(functools.partial(self.client.hincrby, key, increment))

    def hkeys(self, key):
        return self.execute(functools.partial(self.client.hkeys, key))

    def hlen(self, key):
        return self.execute(functools.partial(self.client.hlen, key))

    def hset(self, key, field, value):
        return self.execute(functools.partial(self.client.hset, key, field, value))

    def hsetnx(self, key, field, value):
        return self.execute(functools.partial(self.client.hsetnx, key, field, value))

    def hmset(self, key, mapping):
        return self.execute(functools.partial(self.client.hmset, key, mapping))

    def hmget(self, key, *fields):
        return self.execute(functools.partial(self.client.hmget, key, *fields))

    def hvals(self, key):
        return self.execute(functools.partial(self.client.hvals, key))

    '''
    Glot の都合により追加
    '''
    lindex = index
    llen = len
    incr = addint

    def keys(self, key):
        return self.execute(functools.partial(self.client.keys, key))

    from contextlib import contextmanager
    @contextmanager
    def pipeline(self, *args, **kwargs):
        if connection_pooling:
            SEMA_POOL.acquire()

        try:
            with self.client.pipeline() as pipe:
                yield pipe
        finally:
            if connection_pooling:
                SEMA_POOL.release()
