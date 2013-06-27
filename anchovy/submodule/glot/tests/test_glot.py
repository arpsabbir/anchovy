# -*- coding: utf-8 -*-
"""
Glot のテスト。Redis が起動していないとテスト不可
"""
from __future__ import with_statement

import unittest
import redis
from multiprocessing import Process

from glot.glot import Glot


class TestGlot(unittest.TestCase):
    def setUp(self):
        self.glot = Glot()
        self.fixture = {
            'deck_id': 'event1',
            'shard': '3',
            'player_id': '2',
            'card_and_appearance': [
                ('1', 11),
                ('2', 12),
                ('3', 13)
            ]
        }
        self.fixture['deck_size'] = sum([
            appearance
            for card_id, appearance in self.fixture['card_and_appearance']
        ])
        self.fixture['card_ids'] = [
            card_id
            for card_id, appearance in self.fixture['card_and_appearance']
        ]

    def tearDown(self):
        glot = self.glot
        deck_id, shard, player_id = self._get_fixture(
            'deck_id', 'shard', 'player_id'
        )

        shard = str(int(shard) + 1)
        glot._drop_deck(deck_id, shard, None)
        glot._drop_deck(deck_id, shard, glot._next_current(None))

        glot.clean(deck_id)

    def _get_fixture(self, *names):
        return [self.fixture[name] for name in names]

    def testInitData(self):
        glot = self.glot
        self.assertEqual(glot.kp, 'Glot')
        self.assertIsInstance(glot.r, redis.client.StrictRedis)

    def testKeys(self):
        glot = self.glot
        deck_id, shard, player_id = self._get_fixture(
            'deck_id', 'shard', 'player_id'
        )

        self.assertEqual(
            glot._shard_key(deck_id),
            'Glot:SHARD:%s' % deck_id
        )
        self.assertEqual(
            glot._deck_key(deck_id, shard, None),
            'Glot:DECK:%s:%s' % (deck_id, shard)
        )
        self.assertEqual(
            glot._deck_key(deck_id, shard, 'spam'),
            'Glot:DECK:%s:%s:spam' % (deck_id, shard)
        )
        self.assertEqual(
            glot._position_key(deck_id, player_id),
            'Glot:POSITION:%s:%s' % (deck_id, player_id)
        )
        self.assertEqual(
            glot._deck_hash_key(deck_id),
            'Glot:DECK_HASH:%s' % deck_id
        )
        self.assertEqual(
            glot._deck_current_key(deck_id),
            'Glot:DECK_CURRENT:%s' % deck_id
        )
        self.assertEqual(glot._next_current(None), 'Switch')
        self.assertEqual(glot._next_current('Switch'), None)

        result = []
        glot._do_shard(deck_id, shard, lambda k: result.append(k))
        exprs = ['Glot:DECK:%s:%s' % (deck_id, n)
                 for n in xrange(0, int(shard))]
        self.assertEqual(result, exprs)

    def testReadWriteKVS(self):
        glot = self.glot
        deck_id, player_id = self._get_fixture('deck_id', 'player_id')

        def twice(f):
            for n in xrange(0, 2):
                f(str(n))

        def shard_read_write(n):
            glot._set_shard(deck_id, n)
            self.assertEqual(glot._get_shard(deck_id), n)

        def hash_read_write(n):
            glot._set_deck_hash(deck_id, n)
            self.assertEqual(glot._get_deck_hash(deck_id), n)

        def current_read_write(n):
            glot._set_deck_current(deck_id, n)
            self.assertEqual(glot._get_deck_current(deck_id), n)

        for test_func in [shard_read_write,
                          hash_read_write,
                          current_read_write]:
            twice(test_func)

    def testDrop(self):
        glot = self.glot
        deck_id, shard = self._get_fixture('deck_id', 'shard')

        def assert_drop(current):
            glot._drop_deck(deck_id, shard, current)
            glot._do_shard(
                deck_id, shard,
                lambda key: self.assertEqual(glot.r.llen(key), 0),
                current
            )

        assert_drop(None)
        assert_drop('Switch')

        def set_fixture(current):
            glot._do_shard(
                deck_id, shard,
                lambda key: glot.r.set(key, 'ham,egg'),
                current
            )

        for current in [None, 'Switch']:
            set_fixture(current)
            assert_drop(current)

    def testInsert(self):
        glot = self.glot
        deck_id, shard, card_and_appearance, deck_size = self._get_fixture(
            'deck_id', 'shard', 'card_and_appearance', 'deck_size'
        )

        for current in [None, 'Switch']:
            glot._insert_deck(deck_id, card_and_appearance, shard, current)
            glot._do_shard(
                deck_id, shard,
                lambda key: self.assertEqual(glot.r.llen(key), deck_size),
                current
            )
            self.assertEqual(glot._get_deck_hash(deck_id),
                             glot._make_deck_hash(card_and_appearance))

    def testAllocated(self):
        glot = self.glot
        deck_id, shard, player_id = self._get_fixture(
            'deck_id', 'shard', 'player_id'
        )

        with self.assertRaises(Glot.GetShardError):
            glot._allocated_shard(deck_id, player_id)

        glot._set_shard(deck_id, shard)
        self.assertEqual(
            glot._allocated_shard(deck_id, player_id),
            str(int(player_id) % int(shard))
        )

    def testIncrement(self):
        player_id, = self._get_fixture('player_id')
        self._assert_increment(player_id)

    def testIncrementCommon(self):
        self._assert_increment('common')

    def _assert_increment(self, player_id):
        glot = self.glot
        deck_id, shard, card_and_appearance, deck_size = self._get_fixture(
            'deck_id', 'shard', 'card_and_appearance', 'deck_size'
        )

        glot._set_shard(deck_id, shard)
        allocated_shard = glot._allocated_shard(deck_id, player_id)

        for current in [None, 'Switch']:
            with self.assertRaises(Glot.GetDeckLengthError):
                glot._increment_position(deck_id, allocated_shard,
                                         current, player_id)

            glot._insert_deck(deck_id, card_and_appearance, shard, current)

            init_position = int(glot._increment_position(
                deck_id, allocated_shard, current, player_id))

            self.assertGreaterEqual(init_position, 0)
            self.assertLess(init_position, deck_size)

            for n in xrange(1, deck_size):
                position = glot._increment_position(
                    deck_id, allocated_shard, current, player_id
                )
                self.assertEqual(
                    int(position),
                    (init_position + n) % deck_size
                )

    def testSwitch(self):
        glot = self.glot
        deck_id = self._get_fixture('deck_id')

        glot._switch_deck(deck_id, None)
        self.assertEqual(glot._get_deck_current(deck_id), 'Switch')

        glot._switch_deck(deck_id, 'Switch')
        self.assertEqual(glot._get_deck_current(deck_id), None)

    def testInitAndGet(self):
        glot = self.glot
        deck_id, shard, player_id, \
        card_and_appearance, deck_size, card_ids = self._get_fixture(
            'deck_id', 'shard', 'player_id',
            'card_and_appearance', 'deck_size', 'card_ids'
        )

        with self.assertRaises(Glot.GetShardError):
            glot.get(deck_id, player_id)

        with self.assertRaises(Glot.ShardValueError):
            glot.init(deck_id, card_and_appearance, 0)

        glot.init(deck_id, card_and_appearance, shard)
        self.assertEqual(glot._get_shard(deck_id), shard)

        current = glot._get_deck_current(deck_id)
        self.assertEqual(current, 'Switch')

        glot._do_shard(
            deck_id, shard,
            lambda key: self.assertEqual(glot.r.llen(key), deck_size),
            current
        )

        for n in xrange(0, deck_size * 3):
            self.assertIn(glot.get(deck_id, player_id), card_ids)

    def testReinitHash(self):
        glot = self.glot
        deck_id, shard, card_and_appearance, = self._get_fixture(
            'deck_id', 'shard', 'card_and_appearance',
        )

        def twiceInit(card_and_appearance, shard):
            self.assertEqual(
                glot.init(deck_id, card_and_appearance, shard),
                True)
            self.assertEqual(
                glot.init(deck_id, card_and_appearance, shard),
                False)

        twiceInit(card_and_appearance, shard)

        fixed_shard = str(int(shard) + 1)
        twiceInit(card_and_appearance, fixed_shard)

        fixed_card_and_appearance = card_and_appearance + [(99999, 30)]
        twiceInit(fixed_card_and_appearance, fixed_shard)

        # shard を int で指定
        fixed_shard = int(fixed_shard) + 1
        twiceInit(fixed_card_and_appearance, fixed_shard)

    def testReinitSwitch(self):
        glot = self.glot
        deck_id, shard, player_id, \
        card_and_appearance, deck_size, card_ids = self._get_fixture(
            'deck_id', 'shard', 'player_id',
            'card_and_appearance', 'deck_size', 'card_ids'
        )

        def assertSwitchDeck(shard, expr_current):
            glot.init(deck_id, card_and_appearance, shard)

            current = glot._get_deck_current(deck_id)
            self.assertEqual(current, expr_current)

            glot._do_shard(
                deck_id, shard,
                lambda key: self.assertEqual(glot.r.llen(key), deck_size),
                current
            )

            glot._do_shard(
                deck_id, shard,
                lambda key: self.assertEqual(glot.r.llen(key), 0),
                glot._next_current(current)
            )

            for n in xrange(0, deck_size * 3):
                self.assertIn(glot.get(deck_id, player_id), card_ids)

        assertSwitchDeck(shard, 'Switch')
        assertSwitchDeck(str(int(shard) + 1), None)

    def testGetWhileInit(self):
        glot = self.glot
        deck_id, shard, player_id, \
        card_and_appearance, deck_size, card_ids = self._get_fixture(
            'deck_id', 'shard', 'player_id',
            'card_and_appearance', 'deck_size', 'card_ids'
        )

        def whileInit():
            child_glot = Glot() # Redis のコネクションを親と子で共有しない
            big_card_and_appearance = card_and_appearance * 5000
            child_glot.init(deck_id, big_card_and_appearance, shard)

        glot.init(deck_id, card_and_appearance, shard)

        p = Process(target=whileInit)
        p.start()

        for n in xrange(15000):
            self.assertIn(glot.get(deck_id, player_id), card_ids)

        p.join()


if __name__ == '__main__':
    unittest.main()
