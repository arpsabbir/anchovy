# -*- coding: utf-8 -*-
"""
gtoolkit.redis をテストするための共通処理を提供.
"""

import redis
import threading

def is_redis_running():
    r = redis.StrictRedis()
    try:
        r.get('dummy')
    except:
        return False
    return True

def run_threads(r, threads=10, incr=300, key='spam'):
    ts = [PipeThread(r, i, incr, key) for i in xrange(0, threads)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()

class PipeThread(threading.Thread):
    def __init__(self, r, i, incr, key):
        super(PipeThread, self).__init__()
        self._r = r
        self._i = i
        self._incr = incr
        self._key = key

    def run(self):
        for n in xrange(0, self._incr):
            self._try_incr()

    def _try_incr(self):
        while True: # テストが終わらない事でエラーとする…
            try:
                self._atomic()
                break
            except redis.exceptions.WatchError:
                pass

    def _atomic(self):
        with self._r.pipeline() as pipe:
            pipe.watch(self._key)
            count = pipe.get(self._key)
            if count is None:
                count = 1
            else:
                count = int(count) + 1

            pipe.multi()
            pipe.set(self._key, count)
            pipe.execute()
