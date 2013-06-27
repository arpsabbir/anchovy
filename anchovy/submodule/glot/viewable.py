# -*- coding: utf-8 -*-
"""
箱の中が見えるくじ引き用クラス
"""
from __future__ import with_statement

import redis
import random
import msgpack

from base import GlotBase

class ViewableGlot(GlotBase):
    class GetError(Exception):
        pass

    class CloneError(Exception):
        pass

    class GetDeckError(Exception):
        pass

    class LotError(Exception):
        pass

    class IncrError(Exception):
        pass

    class DecrError(Exception):
        pass

    class DoesNotCardIDError(Exception):
        pass


    def __init__(self,
                 try_clone_count=1000,
                 try_get_count=1000,
                 *args, **kwargs):
        super(ViewableGlot, self).__init__(*args, **kwargs)
        self.try_clone_count = try_clone_count
        self.try_get_count = try_get_count

    def _deck_key(self, deck_id):
        return self._join_keys('VDECK', deck_id)

    def _player_deck_key(self, player_id, deck_id):
        return self._join_keys('VPLAYER_DECK', player_id, deck_id)

    def _pack_and_set(self, key, value, pipe=None):
        if pipe is None:
            pipe = self.r
        pipe.set(key, msgpack.packb(value))

    def _get_and_unpack(self, key, pipe=None):
        if pipe is None:
            pipe = self.r
        value = pipe.get(key)
        if value is None:
            return None
        return msgpack.unpackb(value)

    def _set_deck(self, deck_id, deck, pipe=None):
        self._pack_and_set(self._deck_key(deck_id), deck, pipe)

    def _get_deck(self, deck_id, pipe=None):
        return self._get_and_unpack(self._deck_key(deck_id), pipe)

    def _delete_deck(self, deck_id):
        self.r.delete(self._deck_key(deck_id))

    def _set_player_deck(self, player_id, deck_id, deck, pipe=None):
        self._pack_and_set(self._player_deck_key(player_id, deck_id),
                           deck,
                           pipe)

    def _get_player_deck(self, player_id, deck_id, pipe=None):
        return self._get_and_unpack(self._player_deck_key(player_id, deck_id),
                                    pipe)

    def _delete_player_deck(self, player_id, deck_id, pipe=None):
        if pipe is None:
            pipe = self.r
        return pipe.delete(self._player_deck_key(player_id, deck_id))

    def _transaction_loop(self, count, f, e):
        try_count = 0
        while True:
            try:
                try_count += 1
                result = f()
                break
            except redis.exceptions.WatchError:
                if count < try_count:
                    e()
        return result
        
    def init(self, deck_id, card_and_appearance):
        deck = self._list_to_dict(card_and_appearance)
        self._set_deck(deck_id, deck)

    def _list_to_dict(self, card_and_appearance):
        deck = {}
        for (card_id, appearance) in card_and_appearance:
            deck[card_id] = deck.get(card_id, 0) + int(appearance)
        return deck

    def get(self, deck_id, player_id='common'):
        def f():
            return self._get(deck_id, player_id)

        def e():
            raise self.GetError, (deck_id, player_id)

        return self._transaction_loop(self.try_get_count, f, e)

    def _get(self, deck_id, player_id):
        def _lot(deck):
            card_id = self._lot(deck)
            deck[card_id] -= 1
            return card_id, deck

        return self._update_deck(deck_id, player_id, _lot)

    def _update_deck(self, deck_id, player_id, f):
        with self.r.pipeline() as pipe:
            pipe.watch(self._player_deck_key(player_id, deck_id))

            result, deck = f(self._ensure_get_deck(player_id, deck_id, pipe))

            pipe.multi()

            if self._is_empty_deck(deck):
                deck = None
                self._delete_player_deck(player_id, deck_id, pipe)
            else:
                self._set_player_deck(player_id, deck_id, deck, pipe)
            pipe.execute()
        return result, deck

    def _is_empty_deck(self, deck):
        for (card_id, count) in deck.iteritems():
            if 0 < count:
                return False
        return True

    def _ensure_get_deck(self, player_id, deck_id, pipe=None):
        deck = self._get_player_deck(player_id, deck_id, pipe)
        if deck is not None:
            return deck

        if pipe is not None:
            pipe.watch(self._deck_key(deck_id))

        deck = self._get_deck(deck_id, pipe)
        if deck is not None:
            return deck

        raise self.GetDeckError, deck_id

    def get_candidate(self, deck_id, player_id='common'):
        deck = self._ensure_get_deck(player_id, deck_id)
        return self._lot(deck)

    def _lot(self, deck):
        stairs = self._deck_to_stairs(deck)
        index = random.randint(1, stairs[-1][-1])
        for (card_id, stair) in stairs:
            if index <= stair:
                return card_id
        raise self.LotError

    def _deck_to_stairs(self, deck):
        stairs = []
        stair = 0

        for (card_id, count) in deck.iteritems():
            if 0 < count:
                stair += count
                stairs.append((card_id, stair))

        return stairs

    def decr(self, deck_id, card_id, value, player_id='common'):
        def f():
            return self._incr(deck_id, card_id, int(value) * -1, player_id)

        def e():
            raise self.DecrError, (deck_id, card_id, value, player_id)

        return self._transaction_loop(self.try_clone_count, f, e)

    def incr(self, deck_id, card_id, value, player_id='common'):
        def f():
            return self._incr(deck_id, card_id, int(value), player_id)

        def e():
            raise self.IncrError, (deck_id, card_id, value, player_id)

        return self._transaction_loop(self.try_clone_count, f, e)

    def _incr(self, deck_id, card_id, value, player_id):
        def _update(deck):
            if value < 0 and not deck.has_key(card_id):
                raise self.DoesNotCardIDError, (deck_id, card_id, value,
                                                player_id, deck)

            if deck.has_key(card_id):
                deck[card_id] += value
            else:
                deck[card_id] = value

            if deck[card_id] < 0:
                raise self.DecrError, (deck_id, card_id, value, player_id, deck)

            return None, deck

        result, deck = self._update_deck(deck_id, player_id, _update)
        return deck

    def clone(self, deck_id, player_id='common'):
        def f():
            return self._clone(deck_id, player_id)

        def e():
            raise self.CloneError, (deck_id, player_id)

        return self._transaction_loop(self.try_clone_count, f, e)

    def _clone(self, deck_id, player_id):
        with self.r.pipeline() as pipe:
            pipe.watch(self._deck_key(deck_id))
            pipe.watch(self._player_deck_key(player_id, deck_id))

            deck = self._get_deck(deck_id, pipe)
            if deck is None:
                raise self.GetDeckError, deck_id

            pipe.multi()
            self._set_player_deck(player_id, deck_id, deck, pipe)
            pipe.execute()
        return deck

    def info(self, deck_id, player_id='common'):
        return self._ensure_get_deck(player_id, deck_id)

    def clean(self, deck_id):
        self._delete_deck(deck_id)
        self._delete_keys(self._player_deck_key('*', deck_id))
