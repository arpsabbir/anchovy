# -*- coding: utf-8 -*-
"""
設定を取得するクラス.
"""
class Loader(object):
    def __init__(self):
        try:
            from django.conf import settings
            self._glot = getattr(settings, 'GLOT_SETTINGS', {})
            self._redis = getattr(settings, 'REDIS_DATABASES', {})
        except ImportError:
            self._glot = {}
            self._redis = {}

    def glot_kwargs(self, client):
        kwargs = {
            'key_prefix': self.key_prefix,
            'try_increment_position_max_count': self.try_incr_position_count,
            'position_limit': self.position_limit,
        }
        return self._redis_kwargs(client, kwargs)

    def vlot_kwargs(self, client):
        kwargs = {
            'key_prefix': self.key_prefix,
            'try_clone_count': self.try_clone_count,
            'try_get_count': self.try_get_count,
        }
        return self._redis_kwargs(client, kwargs)

    def _redis_kwargs(self, client, kwargs):
        if client is not None:
            kwargs['client'] = client
            return kwargs

        if self._use_kvs_module_connection == True:
            from kvs.redis_client import get_client
            kwargs['client'] = get_client(name=self._db, setting=self._redis)
            return kwargs

        kwargs['host'] = self.redis_host
        kwargs['port'] = self.redis_port
        kwargs['db'] = self.redis_db
        return kwargs

    @property
    def key_prefix(self):
        return self._glot.get('KEY_PREFIX', '')

    @property
    def try_incr_position_count(self):
        return int(self._glot.get('TRY_INCREMENT_POSITION_COUNT', 10000))

    @property
    def position_limit(self):
        return int(self._glot.get('POSITION_LIMIT', 9999999999))

    @property
    def try_clone_count(self):
        return int(self._glot.get('TRY_CLONE_COUNT', 10000))

    @property
    def try_get_count(self):
        return int(self._glot.get('TRY_GET_COUNT', 10000))

    @property
    def _db(self):
        return self._glot.get('DB', 'glot')

    @property
    def _use_kvs_module_connection(self):
        return self._glot.get('USE_KVS_MODULE_CONNECTION', False)

    @property
    def _redis_conn(self):
        return self._redis.get(self._db, {})

    @property
    def redis_host(self):
        return self._redis_conn.get('HOST', 'localhost')

    @property
    def redis_port(self):
        return int(self._redis_conn.get('PORT', 6379))

    @property
    def redis_db(self):
        return int(self._redis_conn.get('DB', 0))
