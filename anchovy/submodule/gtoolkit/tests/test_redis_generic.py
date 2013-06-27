# -*- coding: utf-8 -*-
"""
gtoolkit.redis.generic のテスト
"""
import unittest

from gtoolkit.tests.redis_tools import is_redis_running

_can_import_gkvs = False
try:
    from gtoolkit.redis.generic import RedisString, RedisArray, RedisHash
    _can_import_gkvs = True
except ImportError, e:
    pass

@unittest.skipUnless(_can_import_gkvs, 'gkvs can not import.')
class TestPool(unittest.TestCase):

    @unittest.skipUnless(is_redis_running(), 'Redis Server is not running on localhost')
    def test_string(self):
        class EggString(RedisString):
            pass


        fixtures = ['spam', 'ham']
        key = 'coffee'

        s1 = EggString.create(key)

        s1.set(fixtures[0])
        self.assertEqual(s1, fixtures[0])

        s1.append(fixtures[1])
        self.assertEqual(s1, ''.join(fixtures))

        s1.store()

        s2 = EggString.create(key)
        self.assertEqual(s2, ''.join(fixtures))

        s3 = s2.client.get('gkvs:generic:String:EggString:' + key)
        self.assertEqual(s3, ''.join(fixtures))

        s2.delete()
        s2.store()

    @unittest.skipUnless(is_redis_running(), 'Redis Server is not running on localhost')
    def test_array(self):
        class EggArray(RedisArray):
            pass


        fixtures = ['spam', 'ham']

        a1 = EggArray.create()
        a1.push(fixtures[0])
        a1.push(fixtures[1])

        self.assertEqual(a1[0], fixtures[0])
        self.assertEqual(a1[1], fixtures[1])

        a1.store()

        a2 = EggArray.create()
        a3 = a2.client.lrange('gkvs:generic:Array:EggArray', 0, -1)
        self.assertEqual(a3, fixtures)

        self.assertEqual(a2.pop(), fixtures[1])
        self.assertEqual(a2.pop(), fixtures[0])
        a2.store()

    @unittest.skipUnless(is_redis_running(), 'Redis Server is not running on localhost')
    def test_hash(self):
        class EggHash(RedisHash):
            pass


        fixture = {'spam': 'foo', 'ham': 'bar'}

        h1 = EggHash.create()
        h1.set('spam', fixture['spam'])
        h1['ham'] = fixture['ham']
        self.assertEqual(h1['spam'], fixture['spam'])
        self.assertEqual(h1.get('ham'), fixture['ham'])
        h1.store()

        h2 = EggHash.create()
        self.assertEqual(h2['spam'], fixture['spam'])
        self.assertEqual(h2.get('ham'), fixture['ham'])

        d = h2.client.hgetall('gkvs:generic:Hash:EggHash')
        self.assertEqual(d, fixture)
 
        h2.clear()
        h2.store()
