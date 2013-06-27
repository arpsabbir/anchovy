# -*- coding: utf-8 -*-
"""
時間関連

Django が依存している pytz をインストールし,
Django Settings に pytz に定義されている適切な TIME_ZONE を設定する事.

例えば日本であれば TIME_ZONE = 'Japan' とする.

now() で django.utils.timezone.get_default_timezone() から返却される
timezone 情報を指定した datetime 値が取得できる.

TIME_ZONE に 'Japan' を指定すると JST+9 が指定された現在時刻が取得できる.
以降の説明は, 全て TIME_ZONE = 'Japan' が指定されていると仮定する.

>>> import gtoolkit
>>> jst_dt = gtoolkit.datetime.now()

datetime で生成した時刻は, 次の様に timezone 情報を追加できる.

>>> import datetime
>>> dt = datetime.datetime.now()
>>> jst_dt = gtoolkit.datetime.localize(dt)

この場合, tzinfo が付加されるだけであるため,
例えば '2012/09/05 10:00' は, '2012/09/05 10:00 JST' となる.

既に timezone 情報として UTC が指定されている場合,
次の様に JST に変換できる.

>>> import pytz
>>> utc_dt = pytz.utc.localize(datetime.datetime.now())
>>> jst_dt = gtoolkit.datetime.normalize(utc_dt)

この場合, tzinfo が変化するため,
例えば '2012/09/05 01:00 UTC' は, '2012/09/05 10:00 JST' となる.

------------
比較について
------------

timezone 情報が正しく付加されているならば, 正しく比較や加減算が可能.
例えば '2012/09/05 01:00 UTC' と, '2012/09/05 10:00 JST' を比較すると
True となる.

>>> utc_dt = pytz.utc.localize(datetime.datetime.now())
>>> jst_dt = gtoolkit.datetime.normalize(utc_dt)
>>> utc_dt == jst_dt # True

------------------------
Django Template について
------------------------

Django Template で, JST を出力したい場合は次の通り::

    {% load tz %}

    {{ value|utc }}

範囲で指定する場合は次の通り::

    {% load tz %}

    {% localtime on %}
        {{ value }}
    {% endlocaltime %}


------------------
Debug 機能について
------------------

Django Settings に DATETIME_NOW_FOR_DEBUG を定義し,
値に '%Y/%m/%d %H:%M:%S' 形式の文字列か,
datetime.datetime のオブジェクトを設定すると,
now() の戻り値が DATETIME_NOW_FOR_DEBUG で指定された値に固定される.

また, datetime.timedelta のオブジェクトを指定すると,
now() の戻り値が datetime.now() に DATETIME_NOW_FOR_DEBUG が加算された値となる.

ローカル端末で安易にデバックを行う場合, datetime.datetime オブジェクトを,
Sandbox 環境でイベントのデバックを行う場合, datetime.timedelta オブジェクトを
それぞれ指定するとよい.
"""

from __future__ import absolute_import

# from gtoolkit import datetime で
# datetime.timedelta が使えるよう timedelta を import しておく.
from datetime import timedelta
from datetime import datetime, date, time

from django.utils.timezone import get_default_timezone
from django.conf import settings

def local_datetime(*args, **kwargs):
    return localize(datetime(*args, **kwargs))

def localize(dt):
    return get_default_timezone().localize(dt)

def normalize(dt):
    return get_default_timezone().normalize(dt)

def now():
    now_for_debug = getattr(settings, 'DATETIME_NOW_FOR_DEBUG', None)

    if type(now_for_debug) in [str, unicode]:
        now = datetime.strptime(now_for_debug, '%Y/%m/%d %H:%M:%S')
    elif isinstance(now_for_debug, datetime):
        now = now_for_debug
    elif isinstance(now_for_debug, timedelta):
        now = datetime.now() + now_for_debug
    else:
        now = datetime.now()

    return localize(now)

def strptime(*args, **kwargs):
    dt = datetime.strptime(*args, **kwargs)
    return localize(dt)

def now_epoch():
    return float(datetime.now().strftime('%s.%f'))

def epoch_to_datetime(epoch):
    return localize(datetime.fromtimestamp(float(epoch)))

def datetime_to_epoch(dt):
    return float(dt.strftime('%s.%f'))

def delta_to_seconds(delta):
    return delta.seconds + delta.microseconds / 1E6 + delta.days * 86400


def expire_date(expire_hour=0, calc_datetime=None):
    """
    日付切り替え時刻を計算する

    :param expire_hour: 切り替え時刻
    :type expire_hour: int

    :param calc_datetime: この時刻を元に計算する指定しない場合は現在
    :type calc_datetime: datetime

    :return:
    :rtype: datetime
    """
    if not calc_datetime:
        calc_datetime = now()

    expire_datetime = datetime.combine(
        normalize(calc_datetime).date(),
        time(hour=expire_hour, tzinfo=get_default_timezone())
    )
    if expire_datetime <= normalize(calc_datetime):
        expire_datetime += timedelta(days=1)

    return expire_datetime
