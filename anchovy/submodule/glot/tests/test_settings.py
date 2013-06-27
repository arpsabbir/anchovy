# -*- coding: utf-8 -*-
"""
Settings のテスト
"""

import unittest

from glot.settings import Loader


class TestSettings(unittest.TestCase):
    def testDefaultConf(self):
        conf = Loader()
        self.assertEqual(conf.key_prefix, '')
        self.assertEqual(conf.try_incr_position_count, 10000)
        self.assertEqual(conf.position_limit, 9999999999)
        self.assertEqual(conf.try_clone_count, 10000)
        self.assertEqual(conf.try_get_count, 10000)
        self.assertEqual(conf._db, 'glot')
        self.assertEqual(conf._use_kvs_module_connection, False)
        self.assertEqual(conf._redis_conn, {})
        self.assertEqual(conf.redis_host, 'localhost')
        self.assertEqual(conf.redis_port, 6379)
        self.assertEqual(conf.redis_db, 0)

    def testConf(self):
        conf = Loader()

        conf._glot = {
            'KEY_PREFIX': 'spam',
            'DB': 'ham',
            'USE_KVS_MODULE_CONNECTION': True,
            'TRY_INCREMENT_POSITION_COUNT': 1,
            'POSITION_LIMIT': 1,
            'TRY_CLONE_COUNT': 1,
            'TRY_GET_COUNT': 1,
        }

        conf._redis = {
            'ham': {
                'HOST': '127.0.0.1',
                'PORT': 11211,
                'DB': 1,
            },
        }

        self.assertEqual(conf.key_prefix, 'spam')
        self.assertEqual(conf.try_incr_position_count, 1)
        self.assertEqual(conf.position_limit, 1)
        self.assertEqual(conf.try_clone_count, 1)
        self.assertEqual(conf.try_get_count, 1)
        self.assertEqual(conf._db, 'ham')
        self.assertEqual(conf._use_kvs_module_connection, True)
        self.assertEqual(conf.redis_host, '127.0.0.1')
        self.assertEqual(conf.redis_port, 11211)
        self.assertEqual(conf.redis_db, 1)

    def testClient(self):
        try:
            import kvs
        except ImportError:
            return

        conf = Loader()

        conf._glot = {
            'USE_KVS_MODULE_CONNECTION': True,
        }

        conf._redis = {
            'glot': {
                'HOST': 'localhost',
            },
        }

        kwargs = conf._redis_kwargs(None, {})
        self.assertIsInstance(kwargs['client'], kvs.redis_client.RedisClient)
