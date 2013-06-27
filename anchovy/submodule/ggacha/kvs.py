# -*- coding: utf-8 -*-
"""
ggacha.logic と ggacha.views 配下のクラスに, KVS 操作機能を提供する.
"""

from __future__ import absolute_import

import msgpack
from datetime import datetime

from ggacha.utils import RaiseExceptionMixin, HasKeyPrefix
from ggacha.redis import HasRedisClientMixin

class KVSMixin(RaiseExceptionMixin):
    """
    Key Vakue Store 操作用の Mix-in クラス.
    
    現在は Redis 接続専用.
    将来的に異なる KVS に切り替える際, この Mix-in クラスだけ修正する予定.

    ggacha.logic と ggacha.views 配下のクラスが Mix-in しているため,
    Logic や View クラスは self.kvs.get() や self.kvs.set() で
    Redis にアクセス可能.

    キーは, ガチャID + ユーザID で一意にしている.

    接続先は, settings.GGACHA_SETTINGS['REDIS_DB'] を使用する.

    .. note::

        gredis, submodules.kvs の順で Redis 接続を取得する.

    .. method:: kvs.get

        キーに紐づいた値を取得する.
        デシリアライザーは msgpack を使用.

        :param string key: キー名. ガチャID + ユーザID + キー名で一意.
        :return: キー名に紐づいた値. 値が無ければ None
        :raises: ImproperlyConfigured

        例外 ImproperlyConfigured は _KVS._key_prefix が未設定で発生する.

        _key_prefix は, gacha_id と player_id から自動生成されるため,
        ImproperlyConfigured 発生時は, gacha_id の設定漏れか
        リクエスト情報からの player_id 取得失敗が考えられる.


    .. method:: kvs.set

        キーに紐づいた値を保存する.
        シリアライザーは msgpack を使用.

        :param string key: キー名. ガチャID + ユーザID + キー名で一意.
        :param object value: msgpack でシリアライズ可能なオブジェクト.
        :raises: ImproperlyConfigured .. 詳細は kvs.get 参照の事.


    .. method:: kvs.delete

        キーに紐づいた値を削除する.

        :param string key: キー名. ガチャID + ユーザID + キー名で一意.
        :raises: ImproperlyConfigured .. 詳細は kvs.get 参照の事.


    .. method:: kvs.get_result

        Logic.do_gacha が return した値を取得する.

        :raises: ImproperlyConfigured .. 詳細は kvs.get 参照の事.
    """

    class _KVS(HasKeyPrefix, HasRedisClientMixin):
        def __init__(self, gacha_id, player_id):
            self.set_key_prefix(gacha_id, player_id)

        def get(self, key):
            self.raise_if_none('_key_prefix')
            value = self.redis.get(self.build_key(key))
            if value is None:
                return None
            return msgpack.unpackb(value)

        def set(self, key, value):
            self.raise_if_none('_key_prefix')
            self.redis.set(self.build_key(key),
                           msgpack.packb(value))

        def delete(self, key):
            self.raise_if_none('_key_prefix')
            self.redis.delete(self.build_key(key))

        def get_result(self):
            return self.get('result')

        def set_result(self, value):
            self.set('result', value)
            self.set_last_gacha_datetime()

        def delete_result(self):
            return self.delete('result')

        def set_last_gacha_datetime(self):
            now = datetime.now()
            self.set('last_gacha_datetime',
                     (now.year, now.month, now.day,
                      now.hour, now.minute, now.second, now.microsecond))

        def get_last_gacha_datetime(self):
            dt_tuple = self.get('last_gacha_datetime')
            return apply(datetime, dt_tuple) if dt_tuple is not None else None


    def init_kvs(self, gacha_id, player_id):
        self._kvs = self._KVS(gacha_id, player_id)

    @property
    def kvs(self):
        self.raise_if_none('_kvs')
        return self._kvs
