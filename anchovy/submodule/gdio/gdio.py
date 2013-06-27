# -*- coding: utf-8 -*-
"""
ゲーム内時間の管理用クラス
"""

import datetime

class gDIO(object):
    class KeyError(Exception):
        pass

    class ValueError(Exception):
        pass

    class CalcSpaceError(Exception):
        pass


    def __init__(self, client, key_prefix=''):
        self._r = client
        self._kp = self.__class__.__name__
        if key_prefix:
            self._kp += ':' + key_prefix

    def _join_keys(self, *names):
        return ':'.join([str(name) for name in (self._kp,) + names])

    def _init_key(self):
        return self._join_keys('INIT_EPOCH')

    def _stop_key(self):
        return self._join_keys('STOP_EPOCH')

    def _get(self, key):
        value = self._r.get(key)
        if value is None:
            raise self.KeyError, key

        try:
            value = float(value)
        except ValueError:
            raise self.ValueError, value

        return datetime.datetime.fromtimestamp(value)

    def _dt_or_now(self, dt=None):
        return dt if dt is not None else datetime.datetime.now()

    def _write_epoch(self, key, dt=None):
        self._r.set(key, self._dt_or_now(dt).strftime('%s.%f'))

    def _delta_to_sec(self, delta):
        # 精度は秒数で良い
        #return delta.seconds + delta.microseconds / 1E6 + delta.days * 86400
        return delta.seconds + delta.days * 86400

    def init(self, init_time=None):
        self._write_epoch(self._init_key(), init_time)

    def stop(self, stop_time=None):
        self._write_epoch(self._stop_key(), stop_time)

    def start(self, start_time=None):
        start_time = self._dt_or_now(start_time)
        init_time = self._get(self._init_key())
        stop_time = self._get(self._stop_key())

        if start_time < stop_time:
            raise self.CalcSpaceError, stop_time, start_time

        stop_delta = start_time - stop_time
        init_time = init_time + stop_delta

        self._r.delete(self._stop_key())
        self.init(init_time=init_time)

    def get(self, now_time=None):
        try:
            stop_time = self._get(self._stop_key())
        except self.KeyError:
            stop_time = None

        if stop_time is None:
            now_time = self._dt_or_now(now_time)
        else:
            now_time = stop_time

        init_time = self._get(self._init_key())

        if now_time < init_time:
            raise self.CalcSpaceError, (init_time, now_time)

        return self._delta_to_sec(now_time - init_time)

    def to_dt(self, sec, init_time=None):
        if init_time is None:
            init_time = self._get(self._init_key())
        return init_time + datetime.timedelta(seconds=sec)

    def to_sec(self, dt, init_time=None):
        if init_time is None:
            init_time = self._get(self._init_key())
        return self._delta_to_sec(dt - init_time)

    def clean(self):
        self._r.delete(self._init_key())
        self._r.delete(self._stop_key())
