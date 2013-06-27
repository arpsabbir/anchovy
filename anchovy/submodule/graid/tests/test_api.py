# -*- coding: utf-8 -*-
"""
Graid API のテスト
"""

import unittest

from graid import (create, attack,
                   get_total_hit_point, get_current_hit_point,
                   get_result, clean)

from graid.tests import trim_datetime

class TestGraid(unittest.TestCase):
    def tearDown(self):
        clean()

    def test_create(self):
        boss_id = create(10, 1)
        self.assertEqual(len(boss_id), 36)
        self.assertEqual(get_total_hit_point(boss_id), 10)
        self.assertEqual(get_current_hit_point(boss_id), 10)

    def test_attack(self):
        boss_id = create(10, 10)

        result, damage, current = attack(boss_id, 'attacker1', 2)
        self.assertTrue(result)
        self.assertEqual(damage, 2)
        self.assertEqual(current, 8)

    def test_result(self):
        boss_id = create(10, 10)

        histories, ranking, assisted = get_result(boss_id)
        self.assertEqual(histories, [])
        self.assertEqual(ranking, [])
        self.assertEqual(assisted, [])

        expr_histories = [('attacker1', 2, 8, None)]
        result, damage, current = attack(boss_id, 'attacker1', 2)

        histories, ranking, assisted = get_result(boss_id)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker1', 2)])
        self.assertEqual(assisted, ['attacker1'])
