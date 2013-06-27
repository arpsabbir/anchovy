# -*- coding: utf-8 -*-
"""
ゲーム内時間の管理を行う.

Redis にストップウォッチを保持しており,
ストップウォッチを参照／操作する API を提供する.

メンテナンスに入る際にストップウォッチを止めると, 
アイテム等の有効期限をメンテナンス時間に応じて延ばす事ができる.

Redis に依存しているため, 使用には Redis Server が必要.

利用方法は次の通り.

>>> import gdio
>>> gdio.init()       # ストップウォッチ作成 & スタート
>>> sec = gdio.get()  # 現在のストップウォッチの秒数を取得
>>> gdio.stop()       # ストップウォッチを止める
>>> gdio.start()      # ストップウォッチをスタート

stop() でストップウォッチを止めている最中に get() を使用すると,
常に stop() した秒数が戻る.

例えば, 有効期限を管理する場合, 秒数を加える事で表現できる.

>>> import time
>>> now_sec = gdio.get() # 現在の秒数
>>> now_sec + 3600       # 一時間追加
>>> time.sleep(3601)
>>> now_sec < gdio.get() # True

ストップウォッチを止めると, 有効期限を延ばせる.

>>> now_sec = gdio.get() # 現在の秒数
>>> now_sec + 3600       # 一時間追加
>>> time.sleep(1800)     # 30 分経過した所で…
>>> gdio.stop()          # ストップウォッチを止める
>>> time.sleep(1801)     # 更に 30 分(+1秒)経過
>>> now_sec < gdio.get() # get() は stop() した秒数が戻るので False
>>> gdio.start()         # ストップウォッチを再開
>>> time.sleep(1801)     # 30 分(+1秒)経過
>>> now_sec < gdio.get() # True

get() で取得した値は, int 型であるため, DB 等に保存して使用できる.

---------------------
Django の設定について
---------------------

Django Settings の記載例は次の通り.

.. code-block:: python

    GDIO_SETTINGS = {
        'KEY_PREFIX': 'gDIO',
        'DB': 'default',
    }


KEY_PREFIX
    Redis に時刻情報を保存する際のキー名の接頭辞.
    省略すると 'gDIO' が使用される.

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

from gdio import gDIO
from conf import gDIOSettings

_memoize_object = threading.local()

def _new():
    obj = getattr(_memoize_object, 'gdio', None)
    if obj is not None:
        return obj

    settings = gDIOSettings()
    r = gredis.get(name=settings.DB)
    obj = gDIO(client=r, key_prefix=settings.KEY_PREFIX)

    setattr(_memoize_object, 'gdio', obj)
    return obj

def init(init_time=None):
    """
    ストップウォッチを作る.

    :param datetime init_time: 初期化時刻. 基本は指定しない事.

    初期化時刻が Redis に設定される.

    init_time を省略すると, 初期化時刻には現在時刻が使用される.

    get() 時の秒数は, 現在時刻 - 初期化時刻 で計算される.
    """
    _new().init(init_time)

def stop(stop_time=None):
    """
    ストップウォッチを止める.

    :param datetime stop_time: 停止時刻. 基本は指定しない事.

    停止時刻が Redis に設定される.

    stop_time を省略すると, 停止時刻には現在時刻が使用される.

    停止中, get() 時の秒数は, 停止時刻 - 初期化時刻 で計算される.
    """
    _new().stop(stop_time)

def start(start_time=None):
    """
    ストップウォッチを再開する.

    :param datetime start_time: 再開時刻. 基本は指定しない事.

    初期化時刻が Redis に再設定される.

    start_time を省略すると, 再開時刻には現在時刻が使用される.

    再設定される初期化時刻は, 初期化時刻 + 再開時刻 - 停止時刻 で計算される.
    """
    _new().start(start_time)

def get(now_time=None):
    """
    ストップウォッチから init() からの経過秒数を取得する.

    :param datetime now_time: 現在時刻. 基本は指定しない事.
    :return: init() からの経過秒数

    now_time を省略すると, 現在時刻が使用される.

    init() からの経過秒数は, 現在時刻 - 初期化時刻 で計算される.

    ただし, 停止中, get() 時の秒数は, 停止時刻 - 初期化時刻 で計算される.
    """
    return _new().get(now_time)

def to_dt(sec, init_time=None):
    """
    指定された秒数を datetime 型に変換する.

    :param int sec: 秒数
    :param datetime init_time: 初期化時刻. 基本は指定しない事.
    :return: 変換後の値(datetime 型)

    init_time を省略すると, init() 時に設定された初期化時刻が使用される.

    datetime 型は, 初期化時刻 + 秒数 で計算される.

    同じ秒数を入れても stop(), start() する度に結果は変化する.

    to_sec() と to_dt() は対となる.
    """
    return _new().to_dt(sec, init_time)

def to_sec(dt, init_time=None):
    """
    指定された datetime 型を秒数に変換する.

    :param datetime dt: 時刻
    :param datetime init_time: 初期化時刻. 基本は指定しない事.
    :return: 変換後の値(int 型)

    init_time を省略すると, init() 時に設定された初期化時刻が使用される.

    秒数は, 時刻 - 初期化時刻で計算される.

    同じ秒数を入れても stop(), start() する度に結果は変化する.

    to_sec() と to_dt() は対となる.
    """
    return _new().to_sec(dt, init_time)

def clean():
    """
    Redis Server から gDIO で使用しているデータを全て削除する.
    """
    _new().clean()
