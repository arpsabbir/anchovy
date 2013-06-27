# -*- coding: utf-8 -*-

#
# KVS種別定義
#

import kvs


KVS_TYPES = {
    "DjangoCache": kvs.DjangoCache,
    "TTObj": kvs.TTObj,
    "TTInt": kvs.TTInt,
    "TTStr": kvs.TTStr,
    "TTObjMP": kvs.TTObjMP,
    "MySQLObj": kvs.MySQLObj,
    "MySQLInt": kvs.MySQLInt,
    "MySQLStr": kvs.MySQLStr,
    "MySQLObjMP": kvs.MySQLObjMP,
    "RedisObj": kvs.RedisObj,
    "RedisInt": kvs.RedisInt,
    "RedisStr": kvs.RedisStr,
    "RedisObjMP": kvs.RedisObjMP,
    "RedisList": kvs.RedisList,
    "RedisHash": kvs.RedisHash,
    "Dummy": kvs.DummyCache,
}
