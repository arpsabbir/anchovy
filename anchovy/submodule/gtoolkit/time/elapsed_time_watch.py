# -*- coding: utf-8 -*-

"""
>>> import time
>>> etw = ElapsedTimeWatch(label='test')
>>> time.sleep(0.001)
>>> result = etw.elapsed_time_lap_ms
>>> assert(result)
>>> assert(isinstance(result, int))
>>> time.sleep(0.001)
>>> assert('test' in etw.log_label)
>>> etw.logging('Phase1')
>>> result = etw.get_log() # u'Total:6ms, Phase1:4ms'
>>> assert('Total' in result and 'Phase1' in result)
>>> etw.write_debug_log()
"""

import logging
import time

from resource import getrusage, RUSAGE_SELF, getpagesize

class ElapsedTimeWatch(object):
    """
    経過時間ロギングツール
    """
    def __init__(self, label=None):
        """
        @param (basestring) label ロギング時に [label] と表示される
        """
        self.start_time = time.time()
        self.latest_time = time.time()
        self.label = label
        self._inner_log = []

        self.start_mem = float(getrusage(RUSAGE_SELF)[6]*getpagesize())
        self.latest_mem = float(getrusage(RUSAGE_SELF)[6]*getpagesize())

    @property
    def elapsed_time(self):
        return time.time() - self.start_time

    @property
    def elapsed_time_ms(self):
        return int(self.elapsed_time * 1000)

    @property
    def elapsed_time_us(self): #microseconds
        return int(self.elapsed_time * 1000000)

    def get_elapsed_time_lap(self):
        r = time.time() - self.latest_time
        self.latest_time = time.time()
        return r

    @property
    def elapsed_time_lap_ms(self):
        return int(self.get_elapsed_time_lap() * 1000)

    @property
    def elapsed_time_lap_us(self):
        return int(self.get_elapsed_time_lap() * 1000000)

    @property
    def elapsed_mem(self):
        return float(getrusage(RUSAGE_SELF)[6]*getpagesize()) - self.start_mem

    @property
    def elapsed_mem_lap(self):
        r = float(getrusage(RUSAGE_SELF)[6]*getpagesize()) - self.latest_mem
        self.latest_mem = float(getrusage(RUSAGE_SELF)[6]*getpagesize())
        return r

    @property
    def elapsed_mem_lap_mb(self):
        return float(self.elapsed_mem_lap / (1024 * 1024))

    @property
    def log_label(self):
        if self.label:
            return u'[ELAPSED_TIME_WATCH:%s] ' % self.label
        else:
            return u'[ELAPSED_TIME_WATCH] '

    def logging_mem(self, message=u''):
        self._inner_log.append(u'%s%s elapsed_time=%dms, lap=%dms[%f]' % (
            self.log_label, message, self.elapsed_time_ms,
            self.elapsed_time_lap_ms, self.elapsed_mem_lap_mb))

    def logging_ms(self, message=u''):
        """
        内部ログに書きこむ
        messageに「ログインボーナス」と入れた場合、「ログインボーナス:29ms」がリストに蓄積される
        """
        self._inner_log.append(u'%s:%dms' % (message, self.elapsed_time_lap_ms,))

    logging = logging_ms

    def logging_us(self, message=u''):
        """
        内部ログに書きこむ us
        """
        self._inner_log.append(u'%s:%dus' % (message, self.elapsed_time_lap_us,))

    def get_log(self):
        return u'Total:%sms, %s' % ( self.elapsed_time_ms , u','.join(self._inner_log))

    def write_debug_log(self, message=u''):
        """ inner_log を logging.debug に書き出す """
        logging.debug(u'[%s] %s: %s' % (self.log_label, message, self.get_log()))