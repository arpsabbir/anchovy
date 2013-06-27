# -*- coding: utf-8 -*-
"""
GTimer のテスト
"""

import unittest
import redis
import datetime
import time

from gtimer.gtimer import GTimer

class TestGTimer(unittest.TestCase):
    def setUp(self):
        self.gt = GTimer(client=redis.StrictRedis())
        self.key = 'ham'
        self.player_id = 'egg'
        self.gt._now = self._now
        self.gt._today = self._today

    def _now(self):
        return datetime.datetime(2012, 1, 5, 12) # week = 3

    def _today(self):
        return datetime.date(2012, 1, 5)

    def tearDown(self):
        self.gt.delete(self.key, self.player_id)

    def test_expire_per_day(self):
        gt = self.gt

        dt = gt._expire_per_day(1)
        self.assertEqual(dt, datetime.datetime(2012, 1, 6, 1))

        dt = gt._expire_per_day(12)
        self.assertEqual(dt, datetime.datetime(2012, 1, 6, 12))

        dt = gt._expire_per_day(13)
        self.assertEqual(dt, datetime.datetime(2012, 1, 5, 13))

    def test_expire_per_week(self):
        gt = self.gt

        dt = gt._expire_per_week(1, None, 12)
        self.assertEqual(dt, datetime.datetime(2012, 1, 10, 12))

        dt = gt._expire_per_week(3, None, 12)
        self.assertEqual(dt, datetime.datetime(2012, 1, 12, 12))

        dt = gt._expire_per_week(3, None, 13)
        self.assertEqual(dt, datetime.datetime(2012, 1, 5, 13))

    def test_expire_per_month(self):
        gt = self.gt

        dt = gt._expire_per_month(1, 12)
        self.assertEqual(dt, datetime.datetime(2012, 2, 1, 12))

        dt = gt._expire_per_month(5, 12)
        self.assertEqual(dt, datetime.datetime(2012, 2, 5, 12))

        dt = gt._expire_per_month(6, 12)
        self.assertEqual(dt, datetime.datetime(2012, 1, 6, 12))

    def test_setnx(self):
        gt = self.gt
        key = self.key
        player_id = self.player_id
        expire_at = datetime.datetime.now() + datetime.timedelta(seconds=1)

        self.assertTrue(gt.setnx(key, player_id, expire_at))
        self.assertFalse(gt.setnx(key, player_id, expire_at))
        self.assertTrue(gt.exists(key, player_id))

        time.sleep(2)
        self.assertFalse(gt.exists(key, player_id))
        self.assertTrue(gt.setnx(key, player_id, expire_at))
