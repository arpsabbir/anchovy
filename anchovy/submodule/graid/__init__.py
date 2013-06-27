# -*- coding: utf-8 -*-
"""
--------
使用方法
--------
レイドバトルの補助を行う.

レースコンディションが発生し易い下記を Redis で管理するための API を提供する.

 - ボスのヒットポイント
 - プレイヤーの攻撃履歴

以下の権限管理を行わないため, 利用者が自ら RDBMS 等で管理する事.

 - 誰のボスか?
 - 誰がボスを攻撃可能か?(プレイヤー間レスキュー依頼)
 - 制限時間内か?(ボスが逃げた!)

また, 本ライブラリで使用する Redis 上のデータには,
全てに有効期限が設けられている.
有効期限内にデータを RDBMS 等に保存しない場合,
レイドバトルの履歴は永遠に失われるため, 注意する事.

利用方法は次の通り.

始めに, 次の様にボスを作る.

>>> import graid
>>> boss_id = graid.create(boss_hp)

この boss_id を RDBMS に保存し, 大切に管理すること.
Django Model であれば, gtoolkit.models の
UniqueIDFieldMixin で追加される unique_id(CharField) に保存できる.
UUID Version 4 を使用しているため, 水平分割されたテーブルに保存できる.

次に, ひたすら殴る. リンチ！リンチ！

>>> is_hit, damage, boss_hp = graid.attack(boss_id, player_id1, damage1)
>>> is_hit, damage, boss_hp = graid.attack(boss_id, player_id2, damage2)
>>> is_hit, damage, boss_hp = graid.attack(boss_id, player_id1, damage3)
>>> is_hit, damage, boss_hp = graid.attack(boss_id, player_id2, damage4)

is_hit
    攻撃がヒットしたか否か.
    既にボスが倒れている場合のみ False が入る.
    False であれば, 既にボスが倒れている旨をプレイヤーに伝える事.

damage
    ボスに与えたダメージ.
    基本的に引数のダメージと同値だが,
    例えば, ヒットポイント 2 のボスに 10 のダメージを与えた場合,
    damage には 2 が入る.

boss_hp
    ダメージを与えた後のボスの現在のヒットポイント

幾つか例を挙げると…

============ =============================================
戻り値       状況
============ =============================================
True, 10, 90 攻撃ヒット, 10ダメージ, 残りヒットポイント 90
True, 100, 0 攻撃ヒット, 100ダメージ, ボスが倒れた
False, 0, 0  既にボスは倒れている
============ =============================================

最後に結果を RDBMS 等の永続化されたストレージに保存する.

>>> histories, ranking, assisted = graid.get_result(boss_id, assisted_rate=10)

histories
    攻撃順にソートされた履歴.
    [(Player ID,
      実際のダメージ,
      ダメージを与えられた後のヒットポイント,
      args,
      日時), ...]

    args は, attack() の第四引数の与えたオブジェクトが入る.
    日時は, attack() を実行した日時が datetime 型で入る.

    histories は, ダメージを与えた順に正しくソートされており,
    各 APP サーバの時刻は考慮されていない.
    故に, 各アプリサーバの時刻がズレている場合,
    histories の並び順は, 日時でソートされていない様に見える.

ranking
    与えたダメージで降順にソートされた player_id のリスト.
    Player ID の重複は存在しない.
    [(Player ID, 総ダメージ), ...]

    MVP のプレイヤーは, 0 番目の要素に入っている.
    ダメージが同値だった場合, player_id の昇順となる.
    MVP を確認する際は, リストの先頭から,
    ダメージが同値か確認を行う必要がある.

assisted
    assisted_rate で指定された割合(%)以上ダメージを与えた player_id のリスト.
    Player ID の重複は存在しない.
    [Player ID, ...]

    並び順は保証されない.

---------------------
Django の設定について
---------------------

Django Settings の記載例は次の通り.

.. code-block:: python

    GRAID_SETTINGS = {
        'KEY_PREFIX': 'Graid',
        'DB': 'default',
    }


KEY_PREFIX
    Redis に時刻情報を保存する際のキー名の接頭辞.
    省略すると 'Graid' が使用される.

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

from graid import Graid
from conf import GraidSettings

_memoize_object = threading.local()

def _new():
    obj = getattr(_memoize_object, 'graid', None)
    if obj is not None:
        return obj

    settings = GraidSettings()
    r = gredis.get(name=settings.DB)
    obj = Graid(redis_client=r, key_prefix=settings.KEY_PREFIX)

    setattr(_memoize_object, 'graid', obj)
    return obj

def create(total_hit_point, expire=86400):
    """
    ボスを作る.

    :param int total_hit_point: ボスの最大ヒットポイント
    :param int expire: データの有効期限(秒数). デフォルト 86400 秒(1日).
    :return: ボスを管理する一意キー
    :raises: TypeError, ValueError

    total_hit_point, expire に
    int 以外の値を与えると TypeError,
    1 以下の値を与えると ValueError となる.

    expire とボスが逃げる事の間に因果関係は無い.
    expire は Redis のメモリ資源を有効活用するためだけに存在する.

    戻り値として返すボスの一意キーを用いて, 他の API 関数を利用するため,
    必ず RDBMS 等の永続化されたストレージに保存する事.
    """
    return _new().create(total_hit_point, expire)

def attack(boss_id, attacker_id, damage_hit_point, args=None):
    """
    ボスを攻撃する.

    :param str boss_id: create() で発行したボスを管理する一意キー
    :param str attacker_id: Player ID
    :param int damage_hit_point: 与えるダメージ
    :param object args: 任意パラメータ
    :return: (成否, 実際に与えたダメージ, ダメージを受けた後のヒットポイント)
    :raises: TypeError, ValueError, KeyError

    存在しない boss_id を指定すると KeyError となる.

    damage_hit_point に
    int 以外の値を与えると TypeError,
    1 以下の値を与えると ValueError となる.

    args は, msgpack で扱えるオブジェクトである事.
    args に指定したオブジェクトは, get_result() で取得できる.

    戻り値の詳細は, 前述参照の事.
    """
    return _new().attack(boss_id, attacker_id, damage_hit_point, args)

def get_total_hit_point(boss_id):
    """
    ボスの最大ヒットポイントを取得する.

    :param str boss_id: create() で発行したボスを管理する一意キー
    :return: 最大ヒットポイント(int)
    :raises: KeyError

    存在しない boss_id を指定すると KeyError となる.
    """
    return _new().get_total_hit_point(boss_id)

def get_current_hit_point(boss_id):
    """
    ボスの現在ヒットポイントを取得する.

    :param str boss_id: create() で発行したボスを管理する一意キー
    :return: 現在のヒットポイント(int)
    :raises: KeyError

    存在しない boss_id を指定すると KeyError となる.
    """
    return _new().get_current_hit_point(boss_id)

def get_result(boss_id, assisted_rate=0):
    """
    結果を取得する.

    :param str boss_id: create() で発行したボスを管理する一意キー
    :param int assisted_rate: 参加と認められるダメージ割合(%)
    :return: 履歴, ダメージランキング, ダメージN%以上
    :raises: KeyError

    存在しない boss_id を指定すると KeyError となる.

    戻り値の詳細は, 前述参照の事.
    """
    return _new().get_result(boss_id, assisted_rate)

def clean():
    """
    本モジュールで使用している全てのデータを Redis から削除する.
    評価用に準備した API であるため, 運用時に実行しない事.
    """
    return _new().clean()
