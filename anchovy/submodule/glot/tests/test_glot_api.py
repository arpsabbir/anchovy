# -*- coding: utf-8 -*-
"""
Glot API のテスト. Redis が起動していないとテスト不可
"""

import unittest

from glot import (init, get, clean, _memoize_object)
from glot.glot import Glot


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glot = Glot()
        cls.deck_id = 'ham'
        cls.shard = '1'
        cls.card_and_appearance = [(n, 25) for n in xrange(1, 5)]
        cls.player_id = 'egg'

    def tearDown(self):
        clean(self.deck_id)
        del _memoize_object.glot

    def testInit(self):
        self._assertInit()

    def _assertInit(self, client=None):
        glot = self.glot
        deck_id = self.deck_id
        shard = self.shard
        card_and_appearance = self.card_and_appearance

        init(deck_id, card_and_appearance, shard, client)
        self.assertEqual(glot._get_shard(deck_id), shard)

        current = glot._get_deck_current(deck_id)
        self.assertEqual(current, 'Switch')

        glot._do_shard(
            deck_id, shard,
            lambda key: self.assertEqual(glot.r.llen(key), 100),
            current
        )

    def testGet(self):
        self._assertGet()

    def _assertGet(self, client=None):
        deck_id = self.deck_id
        shard = self.shard
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        init(deck_id, card_and_appearance, shard, client)

        for n in xrange(0, 300):
            self.assertIn(get(deck_id, player_id, client), ['1', '2', '3', '4'])

    def testKVSClient(self):
        try:
            from kvs.redis_client import get_client
        except ImportError:
            return

        client = get_client(name='glot', setting={'glot': {'HOST': 'localhost'}})
        self._assertInit(client)
        self.tearDown()
        self._assertGet(client)
