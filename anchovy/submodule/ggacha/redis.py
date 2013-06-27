# -*- coding: utf-8 -*-
"""
Redis Cilent 管理
"""
from ggacha.conf import settings

class HasRedisClientMixin(object):
    """
    Redis Client を保持する Mix-in クラス
    """
    @property
    def redis(self):
        if hasattr(self, '_memoize_redis'):
            return self._memoize_redis

        db_name = settings.REDIS_DB

        try:
            import gredis
            self._memoize_redis = gredis.get(db_name)
        except ImportError:
            from kvs.client import get_redis_client
            self._memoize_redis = get_redis_client(db_name).client

        return self._memoize_redis
