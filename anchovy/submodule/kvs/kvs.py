# -*- coding: utf-8 -*-

#
# KVS ラッパークラス
# for Django
#
from django.conf import settings
from django.core.cache import cache

import cPickle as pickle

import client
from horizontal import get_connection_name, is_enable_horizontal_partitioning

CAN_USE_MSGPACK = True
try:
    import msgpack
except ImportError:
    CAN_USE_MSGPACK = False

KEY_DELIMITER = '::'

# settings.pyに項目KVS_KEYNAME_PREFIXを設定すると、キー名の頭にその値が付加される
# 設定例
# KVS_KEYNAME_PREFIX = 'TestApp'

SETTINGS_NAME='KVS_KEYNAME_PREFIX'
DEFAULT_PREFIX = 'App'

# TTクライアントデフォルト設定名
DEFAULT_TYRANT_NAME = 'default'

# MySQLクライアントデフォルト設定名
DEFAULT_MYSQL_NAME = 'default'

# MySQLクライアントデフォルト設定名
DEFAULT_REDIS_NAME = 'default'


# エラー
class Error(Exception):
    pass

class KVSBase(object):
    """
    KVS基底クラス
    """
    KEY_NAME = None # デフォルトキー名
    KEY_FORMAT = '%s' # デフォルトキーフォーマット
    TIMEOUT = None # デフォルトタイムアウト
    def __init__(self, keyvalue=None, keyname=None, keyformat=None, instance=None, timeout=None, **argv):
        self._keyprefix = DEFAULT_PREFIX
        if hasattr(settings, SETTINGS_NAME):
            self._keyprefix = getattr(settings, SETTINGS_NAME)
        if KEY_DELIMITER in self._keyprefix:
            raise Error('Key prefix(%s) in key delimiter(%s)' % (self._keyprefix, KEY_DELIMITER))

        self._keyname = keyname if keyname else self.KEY_NAME
        if not self._keyname:
            self._keyname = self.__class__.__name__
        if KEY_DELIMITER in self._keyname:
            raise Error('Key name(%s) in key delimiter(%s)' % (self._keyname, KEY_DELIMITER))

        self._keyformat = keyformat if keyformat else self.KEY_FORMAT
        if self._keyformat:
            if KEY_DELIMITER in self._keyformat:
                raise Error('Key format(%s) in key delimiter(%s)' % (self._keyformat, KEY_DELIMITER))
            ##print '%s, %s, %s, %s' % (self._keyprefix, self._keyname, self._keyformat, str(keyvalue))
            self._key = self._keyprefix + \
                        KEY_DELIMITER + \
                        self._keyname + \
                        KEY_DELIMITER + \
                        (self._keyformat % keyvalue)
        else:
            raise Error('Require key format.')

        self._instance = instance
        self._timeout = timeout if timeout else self.TIMEOUT

    @property
    def keyformat(self):
        """
        キーフォーマット
        """
        return self._keyformat

    @property
    def keyprefix(self):
        """
        キープリフィックス
        """
        return self._keyprefix

    @property
    def keyname(self):
        """
        キー名
        """
        return self._keyname

    @property
    def key(self):
        """
        キー全体名
        """
        return self._key

    @property
    def instance(self):
        """
        KVSインスタンス
        """
        return self._instance

    @property
    def timeout(self):
        """
        タイムアウト値
        """
        return self._timeout

    def makekey(self, keyvalue):
        """
        キー名を作成して返す
        """
        return self._keyprefix + \
               KEY_DELIMITER + \
               self._keyname + \
               KEY_DELIMITER + \
               (self._keyformat % keyvalue)

    def _getkey(self, keyvalue):
        """
        パラメータに基づいたキー名を返す
        """
        key = self.makekey(keyvalue) if keyvalue else self.key
        return key

    def setkey(self, keyvalue):
        """
        デフォルトキー名設定
        """
        self._key = self.makekey(keyvalue)

    def get(self, default=None, keyvalue=None):
        """
        値の取得
        要オーバーライド
        """
        raise NotImplementedError

    def set(self, value, keyvalue=None):
        """
        値の設定
        要オーバーライド
        """
        raise NotImplementedError

    def add(self, value, keyvalue=None):
        """
        値の加算
        要オーバーライド
        """
        raise NotImplementedError

    def delete(self, keyvalue=None):
        """
        値の削除
        要オーバーライド
        """
        raise NotImplementedError

    """
    アクセッサ
    """
    def _valueset(self, value):
        self.set(value)
    def _valueget(self):
        return self.get(None)
    value = property(_valueget, _valueset)


class TTBase(KVSBase):
    """
    TokyoTyrant 基底 クラス
    """
    SET_NAME = DEFAULT_TYRANT_NAME # デフォルト設定名
    def __init__(self, keyvalue, keyname=None, keyformat=None, set_name=None, **argv):
        tyrant_name = set_name if set_name else self.SET_NAME
        super(TTBase, self).__init__(keyvalue, keyname=keyname, keyformat=keyformat, instance=client.get_tt_client(tyrant_name=tyrant_name), **argv)

    def close(self):
        """
        コネクションを明示的にクローズ
        """
        self.instance.close()

class TTStr(TTBase):
    """
    TokyoTyrant 文字列 クラス
    """
    def get(self, default=None, keyvalue=None):
        return self.instance.get(self._getkey(keyvalue), default)

    def set(self, value, keyvalue=None):
        self.instance.put(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        self.instance.out(self._getkey(keyvalue))

class TTObj(TTBase):
    """
    TokyoTyrant オブジェクト クラス
    """
    def get(self, default=None, keyvalue=None):
        s = self.instance.get(self._getkey(keyvalue), None)
        if s is None:
            return default
        return self._deserialize(s)

    def set(self, value, keyvalue=None):
        s = self._serialize(value)
        self.instance.put(self._getkey(keyvalue), s)

    def delete(self, keyvalue=None):
        self.instance.out(self._getkey(keyvalue))

    def _serialize(self, value):
        return pickle.dumps(value)

    def _deserialize(self, value):
        return pickle.loads(value)

class TTObjMP(TTObj):
    """
    TokyoTyrant オブジェクト クラス
    Msgpackをシリアライザ・デシリアライザとして使用
    """
    def __new__(cls, *args, **argv):
        """
        クラスインスタンス生成
        """
        if not CAN_USE_MSGPACK:
            raise Error('Can not use msgpack')
        return TTObj.__new__(cls, *args, **argv) # デフォルトを返す

    def _serialize(self, value):
        return msgpack.dumps(value)

    def _deserialize(self, value):
        return msgpack.loads(value)

class TTInt(TTBase):
    """
    TokyoTyrant 整数 クラス
    """
    def get(self, default=None, keyvalue=None):
        return self.instance.getint(self._getkey(keyvalue), default)

    def set(self, value, keyvalue=None):
        self.instance.putint(self._getkey(keyvalue), value)

    def add(self, value, keyvalue=None):
        self.instance.addint(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        self.instance.out(self._getkey(keyvalue))

class DjangoCache(KVSBase):
    """
    Django cache クラス
    """
    def __init__(self, keyvalue, keyname=None, keyformat=None, **argv):
        super(DjangoCache, self).__init__(keyvalue, keyname=keyname, keyformat=keyformat, **argv)

    def get(self, default=None, keyvalue=None):
        ret = cache.get(self._getkey(keyvalue))
        if ret is None:
            return default
        return ret

    def set(self, value, keyvalue=None):
        if self.timeout:
            cache.set(self._getkey(keyvalue), value, self.timeout)
        else:
            cache.set(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        cache.set(self._getkey(keyvalue), None, 1) # django.cacheのバグ対処
        ##cache.delete(self._getkey(keyvalue))

class MySQLBase(KVSBase):
    """
    MySQL 基底 クラス
    """
    SET_NAME = DEFAULT_MYSQL_NAME # デフォルト設定名
    def __init__(self, keyvalue, keyname=None, keyformat=None, set_name=None, **argv):
        mysql_name = set_name if set_name else self.SET_NAME
        super(MySQLBase, self).__init__(keyvalue, keyname=keyname, keyformat=keyformat, instance=client.get_mysql_client(name=mysql_name), **argv)

    def close(self):
        """
        コネクションを明示的にクローズ
        """
        self.instance.close()

class MySQLStr(MySQLBase):
    """
    SQL 文字列 クラス
    """
    def get(self, default=None, keyvalue=None):
        return self.instance.get(self._getkey(keyvalue), default)

    def set(self, value, keyvalue=None):
        self.instance.put(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        self.instance.out(self._getkey(keyvalue))

class MySQLObj(MySQLBase):
    """
    MySQL オブジェクト クラス
    """
    def get(self, default=None, keyvalue=None):
        s = self.instance.get(self._getkey(keyvalue), None)
        if s is None:
            return default
        return self._deserialize(s)

    def set(self, value, keyvalue=None):
        s = self._serialize(value)
        self.instance.put(self._getkey(keyvalue), s)

    def delete(self, keyvalue=None):
        self.instance.out(self._getkey(keyvalue))

    def _serialize(self, value):
        return pickle.dumps(value)

    def _deserialize(self, value):
        return pickle.loads(value)

class MySQLObjMP(MySQLObj):
    """
    MySQL オブジェクト クラス
    Msgpackをシリアライザ・デシリアライザとして使用
    """
    def __new__(cls, *args, **argv):
        """
        クラスインスタンス生成
        """
        if not CAN_USE_MSGPACK:
            raise Error('Can not use msgpack')
        return MySQLObj.__new__(cls, *args, **argv) # デフォルトを返す

    def _serialize(self, value):
        return msgpack.dumps(value)

    def _deserialize(self, value):
        return msgpack.loads(value)

class MySQLInt(MySQLBase):
    """
    MySQL 整数 クラス
    """
    def get(self, default=None, keyvalue=None):
        return self.instance.getint(self._getkey(keyvalue), default)

    def set(self, value, keyvalue=None):
        self.instance.putint(self._getkey(keyvalue), value)

    def add(self, value, keyvalue=None):
        self.instance.addint(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        self.instance.out(self._getkey(keyvalue))

class RedisBase(KVSBase):
    """
    Redis 基底 クラス
    """
    SET_NAME = DEFAULT_REDIS_NAME # デフォルト設定名
    def __init__(self, keyvalue, keyname=None, keyformat=None, set_name=None, **argv):
        super(RedisBase, self).__init__(keyvalue, keyname=keyname, keyformat=keyformat, **argv)
        self._init_instance(set_name)

    def _init_instance(self, set_name=None):
        redis_name = get_connection_name(key=self.key, default=set_name if set_name else self.SET_NAME)
        self._instance = client.get_redis_client(name=redis_name)

    def _getkey(self, keyvalue):
        """
        水平分割時にkeyvalueを使った場合はエラーを出す
        """
        if is_enable_horizontal_partitioning() and keyvalue:
            raise Error('cannot use keyvalue with horizontal')
        return super(RedisBase, self)._getkey(keyvalue)

    def setkey(self, keyvalue):
        """
        水平分割時はエラーを出す
        """
        if is_enable_horizontal_partitioning() and keyvalue:
            raise Error('cannot use setkey() with horizontal')
        super(RedisBase, self).setkey(keyvalue)

class RedisStr(RedisBase):
    """
    Redis 文字列 クラス
    """
    def get(self, default=None, keyvalue=None):
        return self.instance.get(self._getkey(keyvalue), default)

    def set(self, value, keyvalue=None):
        self.instance.set(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        self.instance.delete(self._getkey(keyvalue))

class RedisObj(RedisBase):
    """
    Redis オブジェクト クラス
    """
    def get(self, default=None, keyvalue=None):
        s = self.instance.get(self._getkey(keyvalue), None)
        if s is None:
            return default
        return self._deserialize(s)

    def set(self, value, keyvalue=None):
        s = self._serialize(value)
        self.instance.set(self._getkey(keyvalue), s)

    def delete(self, keyvalue=None):
        self.instance.delete(self._getkey(keyvalue))

    def _serialize(self, value):
        return pickle.dumps(value)

    def _deserialize(self, value):
        return pickle.loads(value)

class RedisObjMP(RedisObj):
    """
    Redis オブジェクト クラス
    Msgpackをシリアライザ・デシリアライザとして使用
    """
    def __new__(cls, *args, **argv):
        """
        クラスインスタンス生成
        """
        if not CAN_USE_MSGPACK:
            raise Error('Can not use msgpack')
        return RedisObj.__new__(cls, *args, **argv) # デフォルトを返す

    def _serialize(self, value):
        return msgpack.dumps(value)

    def _deserialize(self, value):
        return msgpack.loads(value)

class RedisInt(RedisBase):
    """
    Redis 整数 クラス
    """
    def get(self, default=None, keyvalue=None):
        return self.instance.getint(self._getkey(keyvalue), default)

    def set(self, value, keyvalue=None):
        self.instance.setint(self._getkey(keyvalue), value)

    def add(self, value, keyvalue=None):
        return self.instance.addint(self._getkey(keyvalue), value)

    def delete(self, keyvalue=None):
        self.instance.delete(self._getkey(keyvalue))

class RedisList(RedisBase):
    """
    Redis List クラス
    """
    def push(self, value, keyvalue=None):
        self.instance.lpush(self._getkey(keyvalue), value)

    def append(self, value, keyvalue=None):
        self.instance.append(self._getkey(keyvalue), value)

    def range(self, start=0, end=-1, keyvalue=None):
        return self.instance.lrange(self._getkey(keyvalue), start, end)

    def len(self, keyvalue=None):
        return self.instance.llen(self._getkey(keyvalue))

    def index(self, idx, keyvalue=None):
        return self.instance.lindex(self._getkey(keyvalue), idx)

    def lset(self, idx, value, keyvalue=None):
        return self.instance.lset(self._getkey(keyvalue), idx, value)

class RedisHash(RedisBase):
    """
    Redis Hash クラス
    """
    def delete(self, fields, keyvalue=None):
        self.instance.hdel(self._getkey(keyvalue), fields)

    def exists(self, field, keyvalue=None):
        return self.instance.hexists(self._getkey(keyvalue), field)

    def get(self, field, keyvalue=None):
        return self.instance.hget(self._getkey(keyvalue), field)

    def getall(self, keyvalue=None):
        return self.instance.hgetall(self._getkey(keyvalue))

    def add(self, field, increment=1, keyvalue=None):
        return self.instance.hincrby(self._getkey(keyvalue), increment)

    def keys(self, keyvalue=None):
        return self.instance.hkeys(self._getkey(keyvalue))

    def length(self, keyvalue=None):
        return self.instance.hlen(self._getkey(keyvalue))

    def set(self, field, value, keyvalue=None):
        self.instance.hset(self._getkey(keyvalue), field, value)

    def setnx(self, field, value, keyvalue=None):
        return self.instance.hsetnx(self._getkey(keyvalue), field, value)

    def mset(self, mapping, keyvalue=None):
        self.instance.hmset(self._getkey(keyvalue), mapping)

    def mget(self, fields, keyvalue=None):
        return self.instance.hmget(self._getkey(keyvalue), fields)

    def values(self, keyvalue=None):
        return self.instance.hvals(self._getkey(keyvalue))

class DummyCache(KVSBase):
    """
    ダミー cache クラス
    実際にはキャッシュを行わない
    """
    def __init__(self, keyvalue, keyname=None, keyformat=None, **argv):
        super(DummyCache, self).__init__(keyvalue, keyname=keyname, keyformat=keyformat, **argv)

    def get(self, default=None, keyvalue=None):
        return default

    def set(self, value, keyvalue=None):
        pass

    def delete(self, keyvalue=None):
        pass

