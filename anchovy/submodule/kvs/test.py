# -*- coding: utf-8 -*-

#
# KVS テストコード
#

from kvs import DjangoCache, TTInt, TTStr, TTObj, DummyCache, TTObjMP, RedisObj, RedisObjMP
from generic import KVS, AttributeKVS, ListKVS

# KVSクラス定義
class TestDjangoCache(DjangoCache):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestTTInt(TTInt):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestTTStr(TTStr):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestTTObj(TTObj):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestDummy(DummyCache):
    KEY_FORMAT = "%d"
class TestTTObjMP(TTObjMP):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestRedisObj(RedisObj):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestRedisObjMP(RedisObjMP):
    KEY_FORMAT = "%d"
    SET_NAME = 'test'
class TestAttributeKVS(AttributeKVS):
    KVS_CLASS = "RedisObjMP"

# 最低限のKVSクラス定義
class TestKVS(KVS):
    KVS_CLASS = "RedisObj"
    SET_NAME = 'test'

def test():
    test_kvs_all()
    test_kvs()
    test_attrkvs()
    test_listkvs()

def test_kvs():
    """
    KVSクラステストコード
    """
    print '=== start test of KVS'
    t = TestKVS('ABC') # キー値'ABC'を指定してインスタンス生成
    print t.key
    t.set(12345) # 値設定
    print t.get() # 値取得
    t.delete() # 値削除

def test_kvs_all():
    """
    KVSクラステストコード
    全てのKVSクラスをテストする
    """
    print '=== start test of primitive kvs all'
    classes = {
        TestDjangoCache: "TEST value",
        TestTTInt: 1234,
        TestTTStr: "TEST value",
        TestTTObj: { "TEST":1234 },
        TestDummy: { "TEST":1234 },
        TestTTObjMP: { "TEST":1234 },
        TestRedisObj: { "TEST":1234 },
        TestRedisObjMP: { "TEST":1234 },
        }

    for cls, value in classes.iteritems():
        for key in xrange(5):
            try:
                kvs = cls(key)
            except ImportError, e:
                print 'can not use kvsclass (%s) skipped.' % str(e)
                break
            print kvs.key
            print kvs.get('default value')
            kvs.set(value)
            print kvs.get()
            kvs.value = value
            print kvs.value
            kvs.delete()
            print kvs.get('default value')

def test_attrkvs():
    """
    AttributeKVSのテスト
    """
    print '=== start test of AttributeKVS'

    att = ('aaa', 'bbb', 'ccc')

    class Player(TestAttributeKVS):
        ATTRIBUTES = att

    d = Player('123')
    d.aaa = 1 # キー 'Player.aaa::123' のKVSに1を設定
    d.bbb = 2
    print 'd.aaa: %d' % d.aaa
    print 'd.bbb: %d' % d.bbb
    print d.attributes()
    d.bbb += 3
    print 'd.bbb: %d' % d.bbb

    x = Player('123')
    print x.attributes()
    print 'x.aaa: %d' % x.aaa
    print 'x.bbb: %d' % x.bbb
    print 'x.ccc: %s' % x.ccc
    d.ccc = 1
    print x.attributes()
    x.deleteall()
    print x.attributes()
    print d.attributes()

    class Player2(TestAttributeKVS):
        ATTRIBUTES = {'aaa': 123, 'bbb': 456, 'x':100 }

    z = Player2('1234')
    z.init_values()
    print z.attributes()
    print 'z.aaa: %d' % z.aaa
    print 'z.bbb: %d' % z.bbb
    print 'z.x: %s' % z.x

    z.deleteall()

    class PlayerCache(AttributeKVS):
        KVS_CLASS = 'DjangoCache'
        ATTRIBUTES = att

    d = PlayerCache('123', timeout=5)
    d.aaa = 1 # キー 'Player.aaa::123' のKVSに1を設定
    d.bbb = 2
    print 'd.aaa: %d' % d.aaa
    print 'd.bbb: %d' % d.bbb
    d.bbb += 3
    print 'd.bbb: %d' % d.bbb
    del d.aaa
    del d.bbb


def test_listkvs():
    """
    ListKVSのテスト
    ListLVSの使用は非推奨
    """
    print '=== start test of ListKVS'
    l = ListKVS('123', keyname='PlayerList', max=3, kvsclass='RedisObjMP') # キー名, 最大項目数を指定
    l.delete()
    l.append(1) # キー 'PlayerList::123' のKVSに1を設定
    l.append(2)
    l.append(3)
    print '%s: %s' % (l.key, l.get())
    l.append(4)
    print '%s: %s' % (l.key, l.get())


    l = ListKVS('123', keyname='PlayerList', max=3, kvsclass='DjangoCache') # キー名, 最大項目数を指定
    l.delete()
    l.append(1) # キー 'PlayerList::123' のKVSに1を設定
    l.append(2)
    l.append(3)
    print '%s: %s' % (l.key, l.get())
    l.append(4)
    print '%s: %s' % (l.key, l.get())

    l.delete()


def thread_test_client():
    k = TestRedisObj(100)
    k.set('TEST')
    k.delete()

def thread_test():
    import time
    import threading
    for i in xrange(100):
        threading.Thread(target=thread_test_client).start()

    time.sleep(10)
