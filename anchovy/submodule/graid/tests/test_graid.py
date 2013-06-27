# -*- coding: utf-8 -*-
"""
Graid のテスト
"""

import unittest
import redis
import time

from graid.graid import Graid

from graid.tests import trim_datetime

class TestGraid(unittest.TestCase):
    def setUp(self):
        self.raid = Graid(redis_client=redis.StrictRedis())

    def tearDown(self):
        self.raid.clean()

    def test_create(self):
        raid = self.raid

        with self.assertRaises(TypeError):
            raid.create('a', 1)

        with self.assertRaises(ValueError):
            raid.create(0, 1)

        with self.assertRaises(TypeError):
            raid.create(10, 'a')

        with self.assertRaises(ValueError):
            raid.create(10, 0)

        boss_id = raid.create(10, 1)
        self.assertEqual(len(boss_id), 36)

        for name in ['total', 'current']:
            method = getattr(raid, 'get_{}_hit_point'.format(name))
            self.assertEqual(method(boss_id), 10)

        self.assertEqual(raid._r.llen(raid._history_key(boss_id)), 1)

        time.sleep(2)
        self.assertIsNone(raid._r.get(raid._boss_key(boss_id)))
        self.assertIsNone(raid._r.get(raid._history_key(boss_id)))

    def test_attack(self):
        raid = self.raid

        with self.assertRaises(KeyError):
            raid.attack('unknown', 'attacker1', 1)

        boss_id = raid.create(10, 10)

        with self.assertRaises(TypeError):
            raid.attack(boss_id, 'attacker1', 'a')

        with self.assertRaises(ValueError):
            raid.attack(boss_id, 'attacker1', -1)

        result, damage, current = raid.attack(boss_id, 'attacker1', 2)
        self.assertTrue(result)
        self.assertEqual(damage, 2)
        self.assertEqual(current, 8)

        result, damage, current = raid.attack(boss_id, 'attacker1', 8)
        self.assertTrue(result)
        self.assertEqual(damage, 8)
        self.assertEqual(current, 0)

        result, damage, current = raid.attack(boss_id, 'attacker1', 1)
        self.assertFalse(result)
        self.assertEqual(damage, 0)
        self.assertEqual(current, 0)
        self.assertEqual(raid._r.hget(raid._boss_key(boss_id), 'current'), '-1')

    def test_attack_over_kill(self):
        raid = self.raid

        boss_id = raid.create(10, 10)

        result, damage, current = raid.attack(boss_id, 'attacker1', 11)
        self.assertTrue(result)
        self.assertEqual(damage, 10)
        self.assertEqual(current, 0)

        result, damage, current = raid.attack(boss_id, 'attacker1', 1)
        self.assertFalse(result)
        self.assertEqual(damage, 0)
        self.assertEqual(current, 0)
        self.assertEqual(raid._r.hget(raid._boss_key(boss_id), 'current'), '-2')

    def test_result(self):
        raid = self.raid

        with self.assertRaises(KeyError):
            return raid.get_result('unknown')

        boss_id = raid.create(10, 10)

        histories, ranking, assisted = raid.get_result(boss_id)
        self.assertEqual(histories, [])
        self.assertEqual(ranking, [])
        self.assertEqual(assisted, [])

        expr_histories = [('attacker1', 2, 8, None)]
        result, damage, current = raid.attack(boss_id, 'attacker1', 2)

        histories, ranking, assisted = raid.get_result(boss_id)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker1', 2)])
        self.assertEqual(assisted, ['attacker1'])

        args = ('spam', 'ham', 'egg')
        expr_histories.append(('attacker1', 2, 6, args))
        result, damage, current = raid.attack(boss_id, 'attacker1', 2, args)

        histories, ranking, assisted = raid.get_result(boss_id)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker1', 4)])
        self.assertEqual(assisted, ['attacker1'])

        expr_histories.append(('attacker2', 2, 4, None))
        result, damage, current = raid.attack(boss_id, 'attacker2', 2)

        histories, ranking, assisted = raid.get_result(boss_id)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker1', 4), ('attacker2', 2)])
        self.assertEqual(assisted, ['attacker1', 'attacker2'])

        expr_histories.append(('attacker2', 4, 0, None))
        result, damage, current = raid.attack(boss_id, 'attacker2', 4)

        histories, ranking, assisted = raid.get_result(boss_id)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker2', 6), ('attacker1', 4)])
        self.assertEqual(assisted, ['attacker2', 'attacker1'])

        result, damage, current = raid.attack(boss_id, 'attacker1', 999)

        histories, ranking, assisted = raid.get_result(boss_id)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker2', 6), ('attacker1', 4)])
        self.assertEqual(assisted, ['attacker2', 'attacker1'])

        histories, ranking, assisted = raid.get_result(boss_id, 60)
        self.assertEqual(trim_datetime(histories), expr_histories)
        self.assertEqual(ranking, [('attacker2', 6), ('attacker1', 4)])
        self.assertEqual(assisted, ['attacker2'])
