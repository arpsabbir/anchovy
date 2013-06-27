# -*- coding: utf-8 -*-
"""
くじ引き用クラス
"""
from __future__ import with_statement

import redis
import random
import hashlib

from base import GlotBase


class Glot(GlotBase):
    class ShardValueError(Exception):
        pass

    class GetShardError(Exception):
        pass

    class GetCardIDError(Exception):
        pass

    class GetDeckLengthError(Exception):
        pass

    class IncrementPositionError(Exception):
        pass


    def __init__(self,
                 try_increment_position_max_count=10000,
                 position_limit=9999999999,
                 *args, **kwargs):
        super(Glot, self).__init__(*args, **kwargs)
        self.incr_max_count = try_increment_position_max_count
        self.position_limit = position_limit

    def _shard_key(self, deck_id):
        return self._join_keys('SHARD', deck_id)

    def _deck_key(self, deck_id, shard, current):
        if current is None:
            return self._join_keys('DECK', deck_id, shard)
        return self._join_keys('DECK', deck_id, shard, current)

    def _position_key(self, deck_id, player_id):
        return self._join_keys('POSITION', deck_id, player_id)

    def _deck_hash_key(self, deck_id):
        return self._join_keys('DECK_HASH', deck_id)

    def _deck_current_key(self, deck_id):
        return self._join_keys('DECK_CURRENT', deck_id)

    def _join_keys(self, *names):
        return ':'.join([str(name) for name in (self.kp,) + names])

    def _do_shard(self, deck_id, shard, f, current=None):
        for n in xrange(0, int(shard)):
            f(self._deck_key(deck_id, n, current))

    def _get_shard(self, deck_id):
        return self.r.get(self._shard_key(deck_id))

    def _set_shard(self, deck_id, shard):
        self.r.set(self._shard_key(deck_id), str(shard))

    def _delete_shard(self, deck_id):
        self.r.delete(self._shard_key(deck_id))

    def _get_deck_hash(self, deck_id):
        return self.r.get(self._deck_hash_key(deck_id))

    def _set_deck_hash(self, deck_id, deck_hash):
        self.r.set(self._deck_hash_key(deck_id), deck_hash)

    def _delete_deck_hash(self, deck_id):
        self.r.delete(self._deck_hash_key(deck_id))

    def _get_deck_current(self, deck_id):
        return self.r.get(self._deck_current_key(deck_id))

    def _set_deck_current(self, deck_id, side_key):
        return self.r.set(self._deck_current_key(deck_id), side_key)

    def _delete_deck_current(self, deck_id):
        return self.r.delete(self._deck_current_key(deck_id))

    def _hash(self, text):
        return hashlib.sha1(text).hexdigest()

    def _next_current(self, old_current):
        return 'Switch' if old_current is None else None

    def init(self, deck_id, card_and_appearance, shard=1):
        """
        glot.api.init 参照の事
        """
        if shard < 1:
            raise Glot.ShardValueError

        if self._need_init(deck_id, card_and_appearance, shard) is False:
            return False

        old_shard = self._get_shard(deck_id)
        old_current = self._get_deck_current(deck_id)
        current = self._next_current(old_current)

        self._insert_deck(deck_id, card_and_appearance, shard, current)
        self._switch_deck(deck_id, old_current)
        self._drop_deck(deck_id, old_shard, old_current)
        return True

    def _need_init(self, deck_id, card_and_appearance, shard):
        old_shard = self._get_shard(deck_id)
        if old_shard != str(shard): # shard 数に変更があれば作り直し
            return True        # 新規であれば shard が None になる

        old_deck_hash = self._get_deck_hash(deck_id)
        deck_hash = self._make_deck_hash(card_and_appearance)

        if old_deck_hash != deck_hash: # 前回とハッシュ値が異なる
            return True
        return False

    def _make_deck_hash(self, card_and_appearance):
        return self._hash(';'.join(
            sorted(((str(card_id) + ':' + str(appearance))
                    for card_id, appearance in card_and_appearance))))

    def _drop_deck(self, deck_id, old_shard, old_current):
        if not old_shard:
            return
        self._do_shard(deck_id, old_shard,
                       lambda key: self.r.delete(key),
                       old_current)

    def _switch_deck(self, deck_id, old_current):
        current = self._next_current(old_current)
        if current is None:
            self._delete_deck_current(deck_id)
        else:
            self._set_deck_current(deck_id, current)

    def _insert_deck(self, deck_id, card_and_appearance, shard, current):
        self._set_shard(deck_id, shard)

        card_ids = []
        for card_id, appearance in card_and_appearance:
            card_ids += [card_id] * int(appearance)

        with self.r.pipeline(transaction=False) as pipe:
            def shuffle_and_push(key):
                random.shuffle(card_ids)
                for card_id in card_ids:
                    pipe.lpush(key, card_id)
                pipe.execute()

            self._do_shard(deck_id, shard, shuffle_and_push, current)

        self._set_deck_hash(deck_id, self._make_deck_hash(card_and_appearance))

    def get(self, deck_id, player_id='common'):
        """
        glot.api.get 参照の事
        """
        shard = self._allocated_shard(deck_id, player_id)
        current = self._get_deck_current(deck_id)
        position = self._increment_position(deck_id, shard, current, player_id)
        card_id = self.r.lindex(self._deck_key(deck_id, shard, current),
                                position)
        if not card_id:
            raise Glot.GetCardIDError
        return card_id

    def _allocated_shard(self, deck_id, player_id):
        shard = self._get_shard(deck_id)
        if not shard:
            raise Glot.GetShardError
        player_hash = self._hash(player_id)
        return str((int(player_hash[-2:], 16) % int(shard)))

    def _increment_position(self, deck_id, shard, current, player_id):
        key = self._position_key(deck_id, player_id)
        len = self.r.llen(self._deck_key(deck_id, shard, current))
        if not len:
            raise Glot.GetDeckLengthError

        if player_id == 'common':
            return self._increment_position_for_common(key, len)
        else:
            return self._increment_position_for_player(key, len)

    def _increment_position_for_common(self, key, len):
        position = self.r.incr(key) - 1
        if self.position_limit < position:
            return self._increment_position_for_player(key, len)
        else:
            return position % len

    def _increment_position_for_player(self, key, len):
        try_count = 0
        while True:
            try:
                try_count += 1
                position = self._increment_position_transaction(key, len)
                break
            except redis.exceptions.WatchError:
                if self.incr_max_count < try_count:
                    raise Glot.IncrementPositionError
        return position

    def _increment_position_transaction(self, key, len):
        with self.r.pipeline() as pipe:
            pipe.watch(key)

            position = pipe.get(key)
            if position is None:
                position = str(random.randint(0, len-1))
            elif int(position) + 1 < len:
                position = str(int(position) + 1)
            else:
                position = '0'

            pipe.multi()
            pipe.set(key, position)
            pipe.execute()
        return position

    def clean(self, deck_id):
        shard = self._get_shard(deck_id)

        # 念のため, 一つ前のデッキも消しておく
        self._drop_deck(deck_id, shard, None)
        self._drop_deck(deck_id, shard, self._next_current(None))

        self._delete_deck_current(deck_id)
        self._delete_deck_hash(deck_id)
        self._delete_shard(deck_id)

        self._delete_keys(self._position_key(deck_id, '*'))
