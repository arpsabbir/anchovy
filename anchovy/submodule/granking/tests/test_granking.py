# -*- coding: utf-8 -*-
"""
GRanking のテスト
"""

import unittest
import redis
import time
from multiprocessing import Process

from granking.granking import GRanking


class TestGRanking(unittest.TestCase):
    def setUp(self):
        self.gr = GRanking(client=redis.StrictRedis())
        self.key = 'ham'

    def tearDown(self):
        self.gr.clean(self.key)

    def test_push_and_get(self):
        gr = self.gr
        key = self.key

        self.assertEqual(gr.get_range(key, 0, 10), [])

        gr.push(key, 'spam', 100)
        gr.push(key, 'egg', 200)

        self.assertEqual(gr.get_range(key, 0, 10), ['egg', 'spam'])
