# -*- coding: utf-8 -*-
"""
抽象くじ引き用クラス
"""
from __future__ import with_statement

import redis

class GlotBase(object):
    def __init__(self,
                 host='localhost', port=6379, db=0,
                 key_prefix='',
                 client=None):
        if client is None:
            self.r = redis.StrictRedis(host=host, port=int(port), db=int(db))
        else:
            self.r = client

        self.kp = key_prefix or self.__class__.__name__

    def _join_keys(self, *names):
        return ':'.join([str(name) for name in (self.kp,) + names])

    def _delete_keys(self, key_pattern):
        keys = self.r.keys(key_pattern)
        with self.r.pipeline(transaction=False) as pipe:
            for key in keys:
                pipe.delete(key)
            pipe.execute()
