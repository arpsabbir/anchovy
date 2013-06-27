# -*- coding: utf-8 -*-
"""
ViewableGlot のテスト。Redis が起動していないとテスト不可
"""
from __future__ import with_statement

import unittest
import copy

from glot.viewable import ViewableGlot


class TestVlot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vlot = ViewableGlot()
        cls.deck_id = 'ham'
        cls.expr_deck = {1: 25, 2: 25, 3: 25, 4: 25}
        cls.card_and_appearance = [(n, 25) for n in xrange(1, 5)]
        cls.expr_stairs = zip(xrange(1, 5), xrange(25, 101, 25))
        cls.player_id = 'egg'

    def tearDown(self):
        vlot = self.vlot
        deck_id = self.deck_id
        vlot.clean(deck_id)

    def testKeys(self):
        vlot = self.vlot
        deck_id = self.deck_id
        player_id = self.player_id

        self.assertEqual(
            vlot._deck_key(deck_id),
            'ViewableGlot:VDECK:{}'.format(deck_id)
        )
 
        self.assertEqual(
            vlot._player_deck_key(player_id, deck_id),
            'ViewableGlot:VPLAYER_DECK:{}:{}'.format(player_id, deck_id)
        )

    def testPackUnpack(self):
        vlot = self.vlot
        key = vlot._deck_key(self.deck_id)
        expr_deck = self.expr_deck

        vlot._pack_and_set(key, expr_deck)
        deck = vlot._get_and_unpack(key)
        self.assertEqual(deck, expr_deck)

    def testDeck(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck

        vlot._set_deck(deck_id, expr_deck)
        deck = vlot._get_deck(deck_id)
        self.assertEqual(deck, expr_deck)

    def testPlayerDeck(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        player_id = self.player_id

        vlot._set_player_deck(player_id, deck_id, expr_deck)
        deck = vlot._get_player_deck(player_id, deck_id)
        self.assertEqual(deck, expr_deck)

        vlot._delete_player_deck(player_id, deck_id)
        deck = vlot._get_player_deck(player_id, deck_id)
        self.assertIsNone(deck)

    def testInit(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        card_and_appearance = self.card_and_appearance

        vlot.init(deck_id, card_and_appearance)
        deck = vlot._get_deck(deck_id)
        self.assertEqual(deck, expr_deck)

    def testListToDict(self):
        vlot = self.vlot
        expr_deck = {1: 50, 2: 50, 3: 50, 4: 50}
        card_and_appearance = self.card_and_appearance * 2

        deck = vlot._list_to_dict(card_and_appearance)
        self.assertEqual(deck, expr_deck)

    def testClone(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        def assertInit(f):
            with self.assertRaises(ViewableGlot.GetDeckError):
                vlot._clone(deck_id, player_id)

            vlot.init(deck_id, card_and_appearance)
            cloned_deck = f()
            self.assertEqual(cloned_deck, expr_deck)
            deck = vlot._get_player_deck(player_id, deck_id)
            self.assertEqual(deck, expr_deck)

        def _init():
            return vlot._clone(deck_id, player_id)

        def init():
            return vlot.clone(deck_id, player_id)

        assertInit(_init)
        self.tearDown()
        assertInit(init)

    def testInfo(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = copy.copy(self.expr_deck)
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        def assertInfo(f):
            with self.assertRaises(ViewableGlot.GetDeckError):
                f()

            vlot.init(deck_id, card_and_appearance)
            deck = f()
            self.assertEqual(deck, expr_deck)

            expr_deck[5] = 25
            vlot._set_player_deck(player_id, deck_id, expr_deck)
            deck = f()
            self.assertEqual(deck, expr_deck)

        def ensure_get_deck():
            with vlot.r.pipeline() as pipe:
                pipe.watch(vlot._player_deck_key(player_id, deck_id))
                deck = vlot._ensure_get_deck(player_id, deck_id, pipe)
            return deck

        def info():
            return vlot.info(deck_id, player_id)

        assertInfo(ensure_get_deck)
        self.tearDown()
        del expr_deck[5]
        assertInfo(info)

    def testDeckToStairs(self):
        vlot = self.vlot
        deck = self.expr_deck
        expr_stairs = self.expr_stairs

        stairs = vlot._deck_to_stairs(deck)
        self.assertEqual(stairs, expr_stairs)

    def testLot(self):
        vlot = self.vlot
        deck = self.expr_deck

        results = {}
        for n in xrange(0, 100):
            card_id = vlot._lot(deck)
            results[card_id] = results.get(card_id, 0) + 1
            self.assertIn(card_id, [1, 2, 3, 4])

        print results # nosetests だと表示されない. 確認したければ直に実行.

    def testEmptyDeck(self):
        vlot = self.vlot
        self.assertFalse(vlot._is_empty_deck({1: 0, 2: 0, 3: 1}))
        self.assertTrue(vlot._is_empty_deck({1: 0, 2: 0, 3: 0}))

    def testGet(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_results = self.expr_deck
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        vlot.init(deck_id, card_and_appearance)

        def assertGet(f):
            results = {}
            for n in xrange(0, 100):
                (card_id, deck) = f()
                results[card_id] = results.get(card_id, 0) + 1
                self.assertIn(card_id, [1, 2, 3, 4])

            self.assertEqual(results, expr_results)
            self.assertIsNone(deck)

        def _get():
            return vlot._get(deck_id, player_id)

        def get():
            return vlot.get(deck_id, player_id)

        assertGet(_get)
        assertGet(get)

    def testIncr(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck.copy()
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        card_id = 1
        value = 1

        vlot.init(deck_id, card_and_appearance)

        expr_deck[card_id] += value
        deck = vlot.incr(deck_id, card_id, value, player_id)
        self.assertEqual(deck, expr_deck)

        deck = vlot.incr(deck_id, 999, value, player_id)
        self.assertEqual(deck[999], value)

    def testDecr(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck.copy()
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        card_id = 1
        value = 1

        vlot.init(deck_id, card_and_appearance)

        with self.assertRaises(ViewableGlot.DoesNotCardIDError):
            deck = vlot.decr(deck_id, 999, value, player_id)

        with self.assertRaises(ViewableGlot.DecrError):
            deck = vlot.decr(deck_id, card_id, 999, player_id)

        expr_deck[card_id] -= value
        deck = vlot.decr(deck_id, card_id, value, player_id)
        self.assertEqual(deck, expr_deck)

        for card_id, value in expr_deck.iteritems():
            deck = vlot.decr(deck_id, card_id, value, player_id)
        self.assertIsNone(deck)

    def testGetCandidate(self):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        vlot.init(deck_id, card_and_appearance)
        for n in xrange(100):
            card_id = vlot.get_candidate(deck_id, player_id)
            self.assertIn(card_id, expr_deck.keys())
