# -*- coding: utf-8 -*-
"""
gtimer のテスト
"""
import datetime
import time

import unittest

from gtimer import exists, delete, setnx

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.key = 'ham'
        self.player_id = 'egg'

    def tearDown(self):
        delete(self.key, self.player_id)

    def test_setnx(self):
        key = self.key
        player_id = self.player_id
        expire_at = datetime.datetime.now() + datetime.timedelta(seconds=1)

        self.assertTrue(setnx(key, player_id, expire_at))
        self.assertFalse(setnx(key, player_id, expire_at))
        self.assertTrue(exists(key, player_id))

        time.sleep(2)
        self.assertFalse(exists(key, player_id))
        self.assertTrue(setnx(key, player_id, expire_at))
