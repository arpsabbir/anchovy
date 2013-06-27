# -*- coding: utf-8 -*-
"""
ViewableGlot API のテスト. Redis が起動していないとテスト不可
"""
from __future__ import with_statement

import unittest

from glot import (vinit, vclone, vinfo, vget, vdecr, vincr,
                  vget_candidate, vclean, _memoize_object)
from glot.viewable import ViewableGlot


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vlot = ViewableGlot()
        cls.deck_id = 'ham'
        cls.expr_deck = {1: 25, 2: 25, 3: 25, 4: 25}
        cls.card_and_appearance = [(n, 25) for n in xrange(1, 5)]
        cls.player_id = 'egg'

    def tearDown(self):
        deck_id = self.deck_id
        vclean(deck_id)
        del _memoize_object.vlot

    def testInit(self):
        self._assertInit()

    def _assertInit(self, client=None):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        card_and_appearance = self.card_and_appearance

        vinit(deck_id, card_and_appearance, client)
        deck = vlot._get_deck(deck_id)
        self.assertEqual(deck, expr_deck)

    def testClone(self):
        self._assertClone()

    def _assertClone(self, client=None):
        vlot = self.vlot
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        with self.assertRaises(ViewableGlot.GetDeckError):
            vclone(deck_id, player_id, client)

        vinit(deck_id, card_and_appearance, client)
        cloned_deck = vclone(deck_id, player_id, client)
        self.assertEqual(cloned_deck, expr_deck)
        deck = vlot._get_player_deck(player_id, deck_id)
        self.assertEqual(deck, expr_deck)

    def testGet(self):
        self._assertGet()

    def _assertGet(self, client=None):
        deck_id = self.deck_id
        expr_results = self.expr_deck
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        vinit(deck_id, card_and_appearance, client)

        results = {}
        for n in xrange(0, 100):
            (card_id, deck) = vget(deck_id, player_id, client)
            results[card_id] = results.get(card_id, 0) + 1
            self.assertIn(card_id, [1, 2, 3, 4])

        self.assertEqual(results, expr_results)
        self.assertIsNone(deck)

    def testInfo(self):
        self._assertInfo()

    def _assertInfo(self, client=None):
        deck_id = self.deck_id
        expr_deck = self.expr_deck
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        vinit(deck_id, card_and_appearance, client)
        deck = vinfo(deck_id, player_id, client)
        self.assertEqual(deck, expr_deck)

    def testDecr(self):
        self._assertDecr()

    def _assertDecr(self, client=None):
        deck_id = self.deck_id
        expr_deck = self.expr_deck.copy()
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        card_id = 1
        value = 1

        vinit(deck_id, card_and_appearance, client)

        expr_deck[card_id] -= value
        deck = vdecr(deck_id, card_id, value, player_id, client)
        self.assertEqual(deck, expr_deck)

        for card_id, value in expr_deck.iteritems():
            deck = vdecr(deck_id, card_id, value, player_id, client)
        self.assertIsNone(deck)

    def testIncr(self):
        self._assertIncr()

    def _assertIncr(self, client=None):
        deck_id = self.deck_id
        expr_deck = self.expr_deck.copy()
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        card_id = 1
        value = 1

        vinit(deck_id, card_and_appearance, client)

        expr_deck[card_id] += value
        deck = vincr(deck_id, card_id, value, player_id, client)
        self.assertEqual(deck, expr_deck)

        deck = vincr(deck_id, 999, value, player_id, client)
        self.assertEqual(deck[999], value)

    def testGetCandidate(self):
        self._assertGetCandidate()

    def _assertGetCandidate(self, client=None):
        deck_id = self.deck_id
        expr_deck = self.expr_deck.copy()
        card_and_appearance = self.card_and_appearance
        player_id = self.player_id

        vinit(deck_id, card_and_appearance, client)
        for n in xrange(100):
            card_id = vget_candidate(deck_id, player_id, client)
            self.assertIn(card_id, expr_deck.keys())

    def testKVSClient(self):
        try:
            from kvs.redis_client import get_client
        except ImportError:
            return

        client = get_client(name='glot', setting={'glot': {'HOST': 'localhost'}})
        self._assertInit(client)
        self.tearDown()
        self._assertClone(client)
        self.tearDown()
        self._assertGet(client)
        self.tearDown()
        self._assertInfo(client)
        self.tearDown()
        self._assertDecr(client)
        self.tearDown()
        self._assertIncr(client)
        self.tearDown()
        self._assertGetCandidate(client)
