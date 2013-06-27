# -*- coding: utf-8 -*-
"""
Glot API のテスト. Redis が起動していないとテスト不可
"""

import unittest

from glot.api import (init, get)
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
        glot = self.glot
        deck_id = self.deck_id
        shard = self.shard
        player_id = self.player_id

        glot._drop_deck(deck_id, shard, None)
        glot._drop_deck(deck_id, shard, glot._next_current(None))
        glot._delete_deck_hash(deck_id)
        glot.r.delete(glot._shard_key(deck_id))
        glot.r.delete(glot._position_key(deck_id, player_id))
        glot._delete_deck_current(deck_id)

    def testInit(self):
        glot = self.glot
        deck_id = self.deck_id
        shard = self.shard
        card_and_appearance = self.card_and_appearance

        init(deck_id, card_and_appearance, shard)
        self.assertEqual(glot._get_shard(deck_id), shard)

        current = glot._get_deck_current(deck_id)
        self.assertEqual(current, 'Switch')

        glot._do_shard(
            deck_id, shard,
            lambda key: self.assertEqual(glot.r.llen(key), 100),
            current
        )

    def testGet(self):
        deck_id = self.deck_id
        shard = self.shard
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        init(deck_id, card_and_appearance, shard)

        for n in xrange(0, 300):
            self.assertIn(get(deck_id, player_id), [1, 2, 3, 4])
