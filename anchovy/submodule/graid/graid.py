# -*- coding: utf-8 -*-
"""
レイド支援クラス
"""

import uuid
import msgpack
import datetime
import pytz

from logger import LoggerMixin

class Graid(LoggerMixin):
    def __init__(self, redis_client, key_prefix='', timezone=None):
        self._r = redis_client
        self._kp = key_prefix

        if timezone is None:
            self._tz = pytz.timezone('Japan')
        else:
            self._tz = timezone

    def _now_epoch(self):
        return datetime.datetime.now().strftime('%s.%f')

    def _epoch_to_datetime(self, epoch):
        return self._tz.localize(datetime.datetime.fromtimestamp(float(epoch)))

    def _join_keys(self, *names):
        return ':'.join([str(name) for name in (self._kp,) + names])

    def _boss_key(self, boss_id):
        return self._join_keys('BOSS', boss_id)

    def _history_key(self, boss_id):
        return self._join_keys('HISTORY', boss_id)

    def _create_boss(self, boss_id, total_hit_point, expire):
        # hset と expire を atomic にする必要はない.
        for field in ['total', 'current']:
            self._r.hset(self._boss_key(boss_id), field, total_hit_point)
        self._r.expire(self._boss_key(boss_id), expire)

    def _decr_boss(self, boss_id, damage_hit_point):
        return self._r.hincrby(self._boss_key(boss_id), 'current',
                               damage_hit_point * -1)

    def _get_boss_field(self, boss_id, field):
        value = self._r.hget(self._boss_key(boss_id), field)
        if value is None:
            raise KeyError, boss_id
        return int(value)

    def _create_history(self, boss_id, expire):
        # dummy データを追加しておかないと, 有効期限を設定できない.
        # push と expire を atomic にする必要はない.
        self._push_history(boss_id, 'dummy', 'dummy', 'dummy', None)
        self._r.expire(self._history_key(boss_id), expire)

    def _push_history(self,
                      boss_id, attacker_id,
                      damage_hit_point, curr_hit_point,
                      args):
        self._r.rpush(self._history_key(boss_id),
                      msgpack.packb((attacker_id,
                                     damage_hit_point,
                                     curr_hit_point,
                                     args,
                                     self._now_epoch())))

    def _assert_int(self, name, target):
        if not isinstance(target, int):
            raise TypeError, name + ' was not INT.'

        if target < 1:
            raise ValueError, name + ' was less than 1.'

    def _trim_hit_point(self, target):
        return 0 if target < 0 else target

    def create(self, total_hit_point, expire=86400):
        # 引数として owner_id をあえて受け取らない. 権限は, 利用者側で管理する.
        self._assert_int('total_hit_point', total_hit_point)
        self._assert_int('expire', expire)

        boss_id = str(uuid.uuid4())
        self._create_boss(boss_id, total_hit_point, expire)
        self._create_history(boss_id, expire)
        self.logger.debug('create(%s)', boss_id)
        return boss_id

    def attack(self, boss_id, attacker_id, damage_hit_point, args=None):
        # 減算失敗で履歴が追加されない事が保証されており,
        # 減算成功の履歴追加順番は適当で良い(ボスの残HPでソート可である)ため,
        # 減算と履歴追加を組み合わせて atomic にする必要はない.
        self._assert_int('damage_hit_point', damage_hit_point)
        self.logger.debug('attack.start(%s): player = %s, damage = %d, args=%s',
                          boss_id, attacker_id, damage_hit_point, repr(args))

        # 存在確認
        curr_hit_point = self.get_current_hit_point(boss_id) # 存在確認
        self.logger.debug('attack.before(%s): hitpoint = %d',
                          boss_id, curr_hit_point)

        curr_hit_point = self._decr_boss(boss_id, damage_hit_point)
        self.logger.debug('attack.after(%s): hitpoint = %d',
                          boss_id, curr_hit_point)

        # 存在確認と減算の間に, 別のプレイヤーが攻撃する場合があるので
        # ここで元のヒットポイントを再計算する.
        prev_hit_point = curr_hit_point + damage_hit_point
        self.logger.debug('attack.before_real(%s): hitpoint = %d',
                          boss_id, prev_hit_point)

        if prev_hit_point <= 0: # Over Kill. ボスは既に倒されている
            self.logger.debug('attack.finish(%s): Over Kill', boss_id)
            return False, 0, 0

        if curr_hit_point < 0:
            damage_hit_point = prev_hit_point

        curr_hit_point = self._trim_hit_point(curr_hit_point)

        self._push_history(boss_id, attacker_id,
                           damage_hit_point, curr_hit_point,
                           args)

        self.logger.debug('attack.finish(%s): damage = %d, hitpoint = %s',
                          boss_id, damage_hit_point, curr_hit_point)
        return True, damage_hit_point, curr_hit_point

    def get_total_hit_point(self, boss_id):
        return self._get_boss_field(boss_id, 'total')

    def get_current_hit_point(self, boss_id):
        return self._trim_hit_point(self._get_boss_field(boss_id, 'current'))

    def get_result(self, boss_id, assisted_rate=0):
        histories = self._histories(boss_id)
        ranking = self._ranking(histories)
        assisted = self._assisted(boss_id, assisted_rate, ranking)
        return histories, ranking, assisted

    def _histories(self, boss_id):
        histories = (msgpack.unpackb(history)
                     for history
                     in self._r.lrange(self._history_key(boss_id), 1, -1))

        def cmp_history(a, b):
            return cmp(b[2], a[2])

        return sorted([(a, b, c, d, self._epoch_to_datetime(epoch))
                       for a, b, c, d, epoch in histories],
                      cmp=cmp_history)

    def _ranking(self, histories):
        damage_of = {}
        for attacker_id, damage_hit_point, a, b, c in histories:
            damage_of[attacker_id] = damage_of.get(attacker_id, 0) + damage_hit_point

        def cmp_damage(a, b):
            # ダメージが同じ場合は, Player ID の昇順
            return cmp(b[1], a[1]) or cmp(a[0], b[0])

        return sorted(damage_of.iteritems(), cmp=cmp_damage)

    def _assisted(self, boss_id, assisted_rate, ranking):
        total_hit_point = self.get_total_hit_point(boss_id)
        assisted_point = int(float(total_hit_point) / 100 * assisted_rate)

        return [attacker_id
                for attacker_id, damage_hit_point in ranking
                if assisted_point <= damage_hit_point]

    def clean(self):
        self._delete_keys(self._boss_key('*'))
        self._delete_keys(self._history_key('*'))

    def _delete_keys(self, key_pattern):
        keys = self._r.keys(key_pattern)
        with self._r.pipeline(transaction=False) as pipe:
            for key in keys:
                pipe.delete(key)
            pipe.execute()
