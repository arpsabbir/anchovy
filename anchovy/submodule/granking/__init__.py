# -*- coding: utf-8 -*-
"""
ランキングの管理を行う.

Redis に依存しているため, 使用には Redis Server が必要.

利用方法は次の通り.

>>> import granking
>>> granking.push('point_ranking', 'player1', 100)
>>> granking.push('point_ranking', 'player2', 200)
>>> granking.push('point_ranking', 'player3', 300)
>>> granking.push('point_ranking', 'player1', 1000)
>>> granking.get('point_ranking') # ['player1', 'player3', 'player2']

---------------------
Django の設定について
---------------------

Django Settings の記載例は次の通り.

.. code-block:: python

    GACTIVELOG_SETTINGS = {
        'KEY_PREFIX': 'app_name',
        'DB': 'default',
        'EXPIRE': 60 * 60 * 24 * 14,
    }


KEY_PREFIX
    Redis にランキングを保存する際のキー名の接頭辞.
    実際に使用される接頭辞は, 'GRanking:' + KEY_PREFIX となる.
    省略すると 'GRanking' のみとなる.

DB
    REDIS_DATABASES のキー名.
    省略すると 'default' が使用される.
    REDIS_DATABASES['キー名'] に設定されている接続情報で
    Redis Server に接続する.

EXPIRE
    キー毎の有効期限. 秒数で指定.
    省略すると, 二週間が使用される.
    get_range() か push() で EXPIRE に指定した値だけ有効期限が延びる.

------------
API 関数詳細
------------
"""

import threading
import gredis

from granking import GRanking
from conf import Settings

_memoize_object = threading.local()

def _new():
    obj = getattr(_memoize_object, 'granking', None)
    if obj is not None:
        return obj

    settings = Settings()
    obj = GRanking(client=gredis.get(name=settings.DB),
                   key_prefix=settings.KEY_PREFIX,
                   expire=settings.EXPIRE,)

    setattr(_memoize_object, 'granking', obj)
    return obj

def push(key, unique_id, value):
    """
    ランキングの更新を行う.

    :param string key: ランキング識別子
    :param string unique_id: ランキングするID. Player ID や Guild ID 等
    :param string value: ランキングのソース値. イベントポイント等
    """
    _new().push(key, unique_id, value)

def get_rank(key, unique_id):
    """
    順位の取得を行う.

    :param string key: ログ識別子
    :param string unique_id: ランキングするID. Player ID や Guild ID 等
    :return: 順位(数値)
    """
    return _new().get_rank(key, unique_id)

def get_range(key, start, end):
    """
    ランキングの範囲取得を行う.

    :param string key: ログ識別子
    :param int start: 添字の開始位置. 0 始まり.
    :param int end: 添字の終了位置. start=0 and end=0 で, 先頭の一件を取得.
    :return: ['push() で指定した unique_id', ...]

    unique_id は文字列化しているので注意.
    """
    return _new().get_range(key, start, end)

def get_count(key):
    """
    件数の取得を行う.

    :param string key: ログ識別子
    :return: 件数(数値)
    """
    return _new().get_count(key)

def touch(key):
    """
    ランキングの有効期限を延長する.

    :param string key: ログ識別子

    push() と get_rank() の内部で自動実行されている.
    """
    _new().touch(key)

def clean(key):
    """
    ランキングを削除する.

    :param string key: ログ識別子
    """
    _new().clean(key)

def gen_list(key, wrapper=None):
    """
    ランキングリストを取得する.

    :param string key: ログ識別子
    :param function wrapper: 要素を包む関数
    :return: GRankingList オブジェクト

    GRankingList は, ある程度 List として振る舞う.
    Django の Paginator に渡す際等に使用する.
    """
    return _new().gen_list(key, wrapper)
