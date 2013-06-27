# -*- coding: utf-8 -*-
"""
gDIO のテスト
"""

import unittest
import datetime
import redis

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

    def _assert_time(self, key, time):
        dio = self.dio
        epoch = dio._r.get(key)
        self.assertEqual(epoch, time.strftime('%s.%f'))

    def test_init(self):
        dio = self.dio
        init_time = self.init_time

        dio.init(init_time)
        self._assert_time(dio._init_key(), init_time)

    def test_stop(self):
        dio = self.dio
        stop_time = self.stop_time

        dio.stop(stop_time)
        self._assert_time(dio._stop_key(), stop_time)

    def test_start(self):
        dio = self.dio
        init_time = self.init_time
        stop_time = self.stop_time
        start_time = self.start_time
        new_init_time = self.new_init_time

        with self.assertRaises(gDIO.KeyError):
            dio.start()

        dio.init(init_time)

        with self.assertRaises(gDIO.KeyError):
            dio.start()

        dio.stop(stop_time)
        dio.start(start_time)
        self.assertIsNone(dio._r.get(dio._stop_key()))
        self._assert_time(dio._init_key(), new_init_time)

    def test_get(self):
        dio = self.dio
        init_time = self.init_time
        stop_time = self.stop_time
        start_time = self.start_time
        new_init_time = self.new_init_time

        with self.assertRaises(gDIO.KeyError):
            dio.get()

        dio.init(init_time)

        now_time = datetime.datetime(2011, 1, 1, 0, 0, 0, 0)
        with self.assertRaises(gDIO.CalcSpaceError):
            dio.get(now_time)

        now_time = datetime.datetime(2012, 1, 1, 1, 0, 0, 0)
        expr_seconds = dio._delta_to_sec(now_time - init_time)
        seconds = dio.get(now_time)
        self.assertEqual(seconds, expr_seconds)

        dio.stop(stop_time)
        now_time = datetime.datetime(2013, 1, 1, 0, 0, 0, 0)
        expr_seconds = dio._delta_to_sec(stop_time - init_time)
        seconds = dio.get(now_time)
        self.assertEqual(seconds, expr_seconds)

        dio.start(start_time)
        expr_seconds = dio._delta_to_sec(now_time - new_init_time)
        seconds = dio.get(now_time)
        self.assertEqual(seconds, expr_seconds)

    def test_to_sec(self):
        dio = self.dio
        init_time = self.init_time
        dt = datetime.datetime(2012, 1, 1, 1, 0, 0, 0)
        expr_sec = dio._delta_to_sec(dt - init_time)

        dio.init(init_time)
        sec = dio.to_sec(dt)
        self.assertEqual(sec, expr_sec)

    def test_to_dt(self):
        dio = self.dio
        init_time = self.init_time
        sec = 3600
        expr_dt = init_time + datetime.timedelta(hours=1)

        dio.init(init_time)
        dt = dio.to_dt(sec)
        self.assertEqual(dt, expr_dt)

    def test_peer(self):
        dio = self.dio
        init_time = self.init_time
        dt = datetime.datetime(2012, 1, 1, 1, 0, 0, 0)

        dio.init(init_time)
        sec = dio.to_sec(dt)
        expr_dt = dio.to_dt(sec)
        self.assertEqual(dt, expr_dt)
