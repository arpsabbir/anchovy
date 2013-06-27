# -*- coding: utf-8 -*-

import unittest
import time

from gtoolkit.time.decorators import debug_elapsed_time
from gtoolkit.time.elapsed_time_watch import ElapsedTimeWatch

class TestTime(unittest.TestCase):

    def test_elapsed_time_watch(self):
        etw = ElapsedTimeWatch(label='test')
        time.sleep(0.001)
        self.assertTrue(etw.elapsed_time)
        self.assertTrue(etw.elapsed_time_ms)
        self.assertTrue(etw.elapsed_time_us)
        self.assertTrue(etw.elapsed_time_lap_ms)
        self.assertTrue(etw.elapsed_time_lap_us)
        _ = etw.elapsed_mem
        _ = etw.elapsed_mem_lap
        _ = etw.elapsed_mem_lap_mb
        time.sleep(0.001)
        self.assertIn('test', etw.log_label)
        etw.logging('Phase1')
        etw.logging_mem()
        etw.logging_ms()
        etw.logging_us()
        result = etw.get_log() # u'Total:6ms, Phase1:4ms'
        self.assertIn('Total', result)
        self.assertIn('Phase1', result)
        etw.write_debug_log()

    def test_debug_elapsed_time(self):
        @debug_elapsed_time
        def func():
           time.sleep(0.001)
        func = debug_elapsed_time(func)
        func() # doctest: +ELLIPSIS
