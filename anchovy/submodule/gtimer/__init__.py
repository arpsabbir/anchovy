# -*- coding: utf-8 -*-
"""
一日一回, 一週間に一回, 一月に一回 等を管理する.

Redis に依存しているため, 使用には Redis Server が必要.

利用方法は次の通り.

>>> import gtimer
>>> key = 'gacha1'
>>> p = 'player1'
>>> gtimer.exists(key, p)  # False
>>> gtimer.per_day(key, p) # True
>>> gtimer.exists(key, p)  # True
>>> gtimer.per_day(key, p) # False


---------------------
Django の設定について
---------------------

Django Settings の記載例は次の通り.

.. code-block:: python

    GTIMER_SETTINGS = {
        'KEY_PREFIX': 'app_name',
        'DB': 'default',
    }


KEY_PREFIX
    Redis に時刻情報を保存する際のキー名の接頭辞.
    実際に使用される接頭辞は, 'GTimer:' + KEY_PREFIX となる.
    省略すると 'GTimer' のみとなる.

DB
    REDIS_DATABASES のキー名.
    省略すると 'default' が使用される.
    REDIS_DATABASES['キー名'] に設定されている接続情報で
    Redis Server に接続する.


------------
API 関数詳細
------------
"""

import threading
import gredis

from gtimer import GTimer
from conf import Settings

_memoize_object = threading.local()

def _new():
    obj = getattr(_memoize_object, 'gtimer', None)
    if obj is not None:
        return obj

    settings = Settings()
    obj = GTimer(client=gredis.get(name=settings.DB),
                 key_prefix=settings.KEY_PREFIX)

    setattr(_memoize_object, 'gtimer', obj)
    return obj

def setnx(key, player_id, expire_at):
    """
    有効期限付きキーを追加する.

    :param string key: 識別子その1
    :param string player_id: 識別子その2
    :param datetime expire_at: キーを削除する日時
    :return: True .. 成功 / False - 失敗

    二時間に一回, 三日に一回等, 複雑なサイクルの際に使用する.

    一回実行すると, 有効期限が切れるまで False を返す.
    """
    return _new().setnx(key, player_id, expire_at)

def per_day(key, player_id, expire_hour=0):
    """
    一日一回だけ成功する setnx の Wrapper

    :param string key: 識別子その1
    :param string player_id: 識別子その2
    :param int expire_hour: キーを削除する時間(0-23)
    :return: True .. 成功 / False - 失敗
    :raises: ValueError

    ValueError
        expire_hour が 0-23 の範囲外
    """
    return _new().per_day(key, player_id, expire_hour)

def per_week(key, player_id,
             expire_weekday=0, expire_isoweekday=None,
             expire_hour=0):
    """
    一週間に一回だけ成功する setnx の Wrapper

    :param string key: 識別子その1
    :param string player_id: 識別子その2
    :param int expire_weekday: キーを削除する曜日(0-6)
    :param int expire_isoweekday: キーを削除する曜日(1-7)
    :param int expire_hour: キーを削除する時間(0-23)
    :return: True .. 成功 / False - 失敗
    :raises: ValueError

    expire_weekday と expire_isoweekday の内, 指定された方を使用する.
    両方指定した際の優先順位は, expire_weekday < expire_isoweekday.

    ValueError
        expire_weekday が 0-6 の範囲外.
        expire_isoweekday が 1-7 の範囲外.
        expire_hour が 0-23 の範囲外.
    """
    return _new().per_week(key, player_id,
                           expire_weekday, expire_isoweekday,
                           expire_hour)

def per_month(key, player_id, expire_day=1, expire_hour=0):
    """
    一月に一回だけ成功する setnx の Wrapper

    :param string key: 識別子その1
    :param string player_id: 識別子その2
    :param int expire_day: キーを削除する日(1-31)
    :param int expire_hour: キーを削除する時間(0-23)
    :return: True .. 成功 / False - 失敗
    :raises: ValueError

    expire_day が, 現在の月の最終日を上回る場合,
    expire_day は, 現在の月の最終日となる.

    例えば, expire_day=31 とした場合, 現在の月が四月であれば,
    per_month 内部で expire_day=30 とする.

    ValueError
        expire_day が 1-31 の範囲外.
        expire_hour が 0-23 の範囲外.
    """
    return _new().per_month(key, player_id, expire_day, expire_hour)

def exists(key, player_id):
    """
    setnx で設定したキーが存在しているか確認を行う.

    :param string key: 識別子その1
    :param string player_id: 識別子その2
    :return: True .. 存在 / False - 未存在
    """
    return _new().exists(key, player_id)

def delete(key, player_id):
    """
    setnx で設定したキーを削除する.

    :param string key: 識別子その1
    :param string player_id: 識別子その2
    """
    _new().delete(key, player_id)
