# -*- coding: utf-8 -*-

import datetime
import calendar

from .logger import LoggerMixin

class GTimer(LoggerMixin):
    def __init__(self, client,
                 key_prefix=None):
        self._r = client
        self._kp = self.__class__.__name__
        if key_prefix is not None:
            self._kp += ':' + key_prefix

    def _join_keys(self, *names):
        return ':'.join([str(name) for name in (self._kp,) + names])

    def _timer_key(self, key, player_id):
        return self._join_keys('TIMER', key, player_id)

    def _combine(self, dt, hour):
        return datetime.datetime.combine(dt, datetime.time(hour=hour))

    def _today(self):
        return datetime.date.today()

    def _now(self):
        return datetime.datetime.now()

    def _validate_hour(self, expire_hour):
        if 0 <= expire_hour <= 23:
            return
        raise ValueError, expire_hour

    def _validate_weekday(self, expire_weekday, expire_isoweekday):
        if expire_isoweekday:
            if 1 <= expire_weekday <= 7:
                return
            raise ValueError, expire_isoweekday

        if 0 <= expire_weekday <= 6:
            return
        raise ValueError, expire_weekday

    def _validate_day(self, expire_day):
        if 1 <= expire_day <= 31:
            return
        raise ValueError, expire_day

    def setnx(self, key, player_id, expire_dt):
        timer_key = self._timer_key(key, player_id)
        if not self._r.setnx(timer_key, 'x'):
            return False

        self._r.expireat(timer_key, expire_dt)
        self.logger.debug({'setnx': {'key': timer_key, 'dt': expire_dt,},})
        return True

    def per_day(self, key, player_id, expire_hour=0):
        self._validate_hour(expire_hour)
        expire_dt = self._expire_per_day(expire_hour)
        return self.setnx(key, player_id, expire_dt)

    def _expire_per_day(self, expire_hour):
        expire_dt = self._combine(self._today(), expire_hour)
        if expire_dt <= self._now():
            expire_dt += datetime.timedelta(days=1)
        return expire_dt

    def per_week(self, key, player_id,
                 expire_weekday=0,
                 expire_isoweekday=None,
                 expire_hour=0):
        self._validate_weekday(expire_weekday, expire_isoweekday)
        expire_dt = self._expire_per_week(expire_weekday,
                                          expire_isoweekday,
                                          expire_hour)
        return self.setnx(key, player_id, expire_dt)

    def _expire_per_week(self, expire_weekday, expire_isoweekday, expire_hour):
        if expire_isoweekday:
            expire_weekday = expire_isoweekday - 1

        today = self._today()
        weekday = today.weekday()
        monday = today - datetime.timedelta(days=weekday)
        expire_date = monday + datetime.timedelta(days=expire_weekday)
        expire_dt = self._combine(expire_date, expire_hour)

        if self._now() < expire_dt:
            return expire_dt

        expire_dt += datetime.timedelta(weeks=1)
        return expire_dt

    def per_month(self, key, player_id, expire_day=1, expire_hour=0):
        self._validate_day(expire_day)
        self._validate_hour(expire_hour)
        expire_dt = self._expire_per_month(expire_day, expire_hour)
        return self.setnx(key, player_id, expire_dt)

    def _expire_per_month(self, expire_day, expire_hour):
        today = self._today()
        weekday, last_day = calendar.monthrange(today.year, today.month)

        if last_day < expire_day:
            expire_day = last_day

        expire_date = datetime.date(today.year, today.month, expire_day)
        expire_dt = self._combine(expire_date, expire_hour)

        if self._now() < expire_dt:
            return expire_dt

        last_date = datetime.date(today.year, today.month, last_day)
        next_date = last_date + datetime.timedelta(days=1)
        weekday, last_day = calendar.monthrange(next_date.year, next_date.month)

        if last_day < expire_day:
            expire_day = last_day

        expire_date = datetime.date(next_date.year, next_date.month, expire_day)
        return self._combine(expire_date, expire_hour)

    def exists(self, key, player_id):
        timer_key = self._timer_key(key, player_id)
        return self._r.exists(timer_key)

    def delete(self, key, player_id):
        timer_key = self._timer_key(key, player_id)
        self._r.delete(timer_key)
