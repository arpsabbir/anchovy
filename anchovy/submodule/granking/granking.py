# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger('granking')

_2WEEKS = 60 * 60 * 24 * 14

class GRanking(object):
    def __init__(self, client, key_prefix=None, expire=_2WEEKS):
        self._r = client
        self._kp = self.__class__.__name__
        if key_prefix is not None:
            self._kp += ':' + key_prefix
        self._expire = expire

    def _join_keys(self, *names):
        return ':'.join([str(name) for name in (self._kp,) + names])

    def _key(self, key):
        return self._join_keys('KEY', key)

    def push(self, key, unique_id, value):
        _logger.debug(u'push(%s, %s, %s)', key, unique_id, value)
        self._r.zadd(self._key(key), long(value), unique_id)
        self.touch(key)

    def get_rank(self, key, unique_id):
        rank = self._r.zrevrank(self._key(key), unique_id)
        if rank is None:
            _logger.debug(u'get_rank(%s, %s) = %s', key, unique_id, rank)
            return None

        value = self._r.zscore(self._key(key), unique_id)
        for n in xrange(self.get_count(key)):
            if rank <= 0:
                break
            rank -= 1

            upper_id = self.get_range(key, rank, rank)[0]
            upper_value = self._r.zscore(self._key(key), upper_id)

            _logger.debug(u'upper: %s %s', upper_id, upper_value)
            if value < upper_value:
                rank += 1
                break

        # 順位を取得するため, 添字に 1 を加える
        rank += 1
        _logger.debug(u'get_rank(%s, %s) = %s', key, unique_id, rank)
        return rank

    def get_range(self, key, start, end):
        result = self._r.zrevrange(self._key(key), start, end)
        _logger.debug(u'get_range(%s, %s, %s) = %s', key, start, end, result)
        self.touch(key)
        return result

    def get_count(self, key):
        count = self._r.zcard(self._key(key))
        _logger.debug(u'get_count(%s) = %s', key, count)
        return count

    def touch(self, key):
        _logger.debug(u'touch(%s)', key)
        self._r.expire(self._key(key), self._expire)

    def clean(self, key):
        _logger.debug(u'clean(%s)', key)
        self._r.delete(self._key(key))

    def gen_list(self, key, wrapper=None):
        _logger.debug(u'gen_list(%s)', key)
        return _GRankingList(self, key, wrapper)


class _GRankingList(object):
    def __init__(self, grank, key, wrapper=None):
        self._grank = grank
        self._key = key
        self._wrapper = wrapper

    def __getitem__(self, k):
        _logger.debug(u'__getitem__(%s)', k)
        if isinstance(k, slice):
            start = k.start if k.start else 0
            end = k.stop - 1 if k.stop else self.__len__() - 1
            step = k.step

            unique_ids = self._grank.get_range(self._key, start, end)
            if step:
                unique_ids = unique_ids[::step]

            return [self._wrap(unique_id) for unique_id in unique_ids]
        else:
            if self.__len__() <= k:
                raise IndexError('list index out of range')
            unique_ids = self._grank.get_range(self._key, k, k)
            return self._wrap(unique_ids[0])

    def _wrap(self, unique_id):
        return self._wrapper(unique_id) if self._wrapper else unique_id

    def __len__(self):
        _logger.debug(u'__len__()')
        return self._grank.get_count(self._key)
