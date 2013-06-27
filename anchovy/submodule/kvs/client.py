# -*- coding: utf-8 -*-

from django.conf import settings

def get_tt_client(tyrant_name=None):
    """
    TTクライアント取得
    """
    from tokyotyrant import get_client
    return get_client(tyrant_name=tyrant_name)

def get_mysql_client(name=None):
    """
    MySQLクライアント取得
    """
    from mysqlkvs import get_client
    return get_client(name=name, setting=settings.MYSQLKVS_DATABASES)

def get_redis_client(name=None):
    """
    Redisクライアント取得
    """
    from redis_client import get_client
    return get_client(name=name, setting=settings.REDIS_DATABASES)
