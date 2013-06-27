# -*- coding: utf-8 -*-
"""
gdio のテスト
"""

import unittest
import datetime
import redis

from gdio import _new, init, stop, start, get, to_dt, to_sec
from gdio.gdio import gDIO


class TestGDIO(unittest.TestCase):
    def setUp(self):
        self.dio = gDIO(client=redis.StrictRedis())
        self.init_time = datetime.datetime(2012, 1, 1, 0, 0, 0, 0)
        self.stop_time = datetime.datetime(2012, 1, 1, 2, 0, 0, 0)
        self.start_time = datetime.datetime(2012, 1, 1, 3, 0, 0, 0)

        stop_delta = self.start_time - self.stop_time
        self.new_init_time = self.init_time + stop_delta

    def tearDown(self):
        self.dio.clean()

    def _assertTime(self, key, time):
        dio = self.dio
        epoch = dio._r.get(key)
        self.assertEqual(epoch, time.strftime('%s.%f'))

    def test_init(self):
        dio = self.dio
        init_time = self.init_time

        init(init_time)
        self._assertTime(dio._init_key(), init_time)

    def test_stop(self):
        dio = self.dio
        stop_time = self.stop_time

        stop(stop_time)
        self._assertTime(dio._stop_key(), stop_time)

    def test_start(self):
        dio = self.dio
        init_time = self.init_time
        stop_time = self.stop_time
        start_time = self.start_time
        new_init_time = self.new_init_time

        with self.assertRaises(gDIO.KeyError):
            start()

        init(init_time)

        with self.assertRaises(gDIO.KeyError):
            start()

        stop(stop_time)
        start(start_time)
        self.assertIsNone(dio._r.get(dio._stop_key()))
        self._assertTime(dio._init_key(), new_init_time)

    def test_get(self):
        init_time = self.init_time
        stop_time = self.stop_time
        start_time = self.start_time
        new_init_time = self.new_init_time

        with self.assertRaises(gDIO.KeyError):
            get()

        init(init_time)

        now_time = datetime.datetime(2011, 1, 1, 0, 0, 0, 0)
        with self.assertRaises(gDIO.CalcSpaceError):
            get(now_time)

        now_time = datetime.datetime(2012, 1, 1, 1, 0, 0, 0)
        expr_seconds = _new()._delta_to_sec(now_time - init_time)
        seconds = get(now_time)
        self.assertEqual(seconds, expr_seconds)

        stop(stop_time)
        now_time = datetime.datetime(2013, 1, 1, 0, 0, 0, 0)
        expr_seconds = _new()._delta_to_sec(stop_time - init_time)
        seconds = get(now_time)
        self.assertEqual(seconds, expr_seconds)

        start(start_time)
        expr_seconds = _new()._delta_to_sec(now_time - new_init_time)
        seconds = get(now_time)
        self.assertEqual(seconds, expr_seconds)

    def test_to_sec(self):
        init_time = self.init_time
        dt = datetime.datetime(2012, 1, 1, 1, 0, 0, 0)
        expr_sec = _new()._delta_to_sec(dt - init_time)

        init(init_time)
        sec = to_sec(dt)
        self.assertEqual(sec, expr_sec)

    def test_to_dt(self):
        init_time = self.init_time
        sec = 3600
        expr_dt = init_time + datetime.timedelta(hours=1)

        init(init_time)
        dt = to_dt(sec)
        self.assertEqual(dt, expr_dt)

    def test_peer(self):
        init_time = self.init_time
        dt = datetime.datetime(2012, 1, 1, 1, 0, 0, 0)

        init(init_time)
        sec = to_sec(dt)
        expr_dt = to_dt(sec)
        self.assertEqual(dt, expr_dt)
