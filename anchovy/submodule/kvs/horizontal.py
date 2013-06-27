# -*- coding: utf-8 -*-

from django.conf import settings

import hashlib

DEFAULT_DB_NAME_FORMAT = 'shard%d'
KVS_SETTINGS_DEFAULT_DB_NAME_FORMAT = 'KVS_HORIZONTAL_PARTITIONING_DB_NAME_FORMAT'
KVS_SETTINGS_DEFAULT_HORIZONTAL_PARTITIONING_ENABLE = 'KVS_HORIZONTAL_PARTITIONING_ENABLE'


def is_enable_horizontal_partitioning():
    return bool(getattr(settings, KVS_SETTINGS_DEFAULT_HORIZONTAL_PARTITIONING_ENABLE) if hasattr(settings, KVS_SETTINGS_DEFAULT_HORIZONTAL_PARTITIONING_ENABLE) else False)

def get_connection_name(key=None, set_name=None, default=None):

    # 指定があるなら優先
    if set_name:
        return set_name

    # 水平分割が有効でなければdefaultを返す
    if not is_enable_horizontal_partitioning():
        return default

    return get_horizontal_partitioning_database_name(key) if key else None



def get_horizontal_partitioning_database_name(key_name):
    """
    MySQL用水平分割関数をとりあえずRedis用に変数などを調整したもの

    user_id (osuser_id, player_id)からハッシュDB名を返す
    user_id は str でも unicode でも同じ値になる

    MySQLでデータマイグレーションを行う場合は、
    SELECT CONV(RIGHT(SHA1('USER-ID'),1), 16, 10); や
    SELECT MOD(CONV(RIGHT(SHA1('USER-ID'),2), 16, 10), 16); という感じで行う

    >>> from horizontalpartitioning import get_horizontal_partitioning_database_name
    >>> get_horizontal_partitioning_database_name('12346')
    'part2'
    >>> get_horizontal_partitioning_database_name(u'12346')
    'part2'
    >>> get_horizontal_partitioning_database_name(12346)
    TypeError: must be string or buffer, not int
    """
    key_name = str(key_name) if isinstance(key_name, (int, long)) else key_name
    hex_hash = hashlib.sha1(key_name).hexdigest()
    group_number = (int(hex_hash[-2:], 16) % settings.KVS_HORIZONTAL_PARTITIONING_NUMBER)
    #▲ハッシュ文字列の下2桁を16進数にしてDB振り分け。256台まではこれで大丈夫。スライスした方がちょっとだけ早かった
    #むしろ下1桁だけ見ればいい気もするが、ローカルで%4などで使うケースもあるのでこれで良い
    name_format = getattr(settings, KVS_SETTINGS_DEFAULT_DB_NAME_FORMAT) if hasattr(settings, KVS_SETTINGS_DEFAULT_DB_NAME_FORMAT) else DEFAULT_DB_NAME_FORMAT
    return name_format % group_number


