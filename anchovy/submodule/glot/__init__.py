# -*- coding: utf-8 -*-
"""
.. module:: glot

.. moduleauthor:: Masahito Ikuta <masahito.ikuta@gu3.co.jp>

----------------------------
シャッフルされたデッキ(Glot)
----------------------------

デッキの中(Redis)にカードをシャッフルしてデッキ(Redis)に積んでおき,
利用者に上から一枚引いてもらう…というのが大雑把なイメージ.

Redis が起動していれば ./manage.py shell で動作確認が可能.

>>> from glot import init, get
>>> init('event1', [('1', '10'), (2, 20), ('3', 30)])
>>> [get('event1') for x in xrange(0, 100)]

デッキ内のカードは, ランダムにシャッフルされた状態で配列として保存されており, 
get() で配列の先頭から末尾に向かって 1 枚ずつカードを取得して行く.

カードの取得は, 配列から要素を pop するのではなく,
現在の参照位置を加算する事で行われる.
そのため, 参照位置が末尾に達した場合,
また配列の先頭に戻ってカードを取得し続ける.
よって, 一度デッキを作るとカードは尽きる事がない.

プレイヤー毎にデッキを用意する事も可能.
詳細は, 本ドキュメント内の関数の説明を参照の事.

------------------------------
カード残数が見えるデッキ(Vlot)
------------------------------

基本的なイメージは Glot と同様.
ただし, 現在のデッキの状態を取得する事ができる.

vinit() は init() より早い.
しかし, カードを引く度に計算(シリアライズ, デシリアライズ, 乱数生成)が行われるため, vget() は get() より遅い.
また, 全プレイヤーで共通のデッキを Vlot で作ると, vget() の失敗率が上昇する.
よって, 全ユーザで共通のデッキは Glot を,
ユーザ毎に作成するデッキは Vlot を使用すると良い.

.. note:

    Glot と Vlot では空間効率に違いがある.

    Glot は, init() で全プレイヤーで共有する巨大な配列を作るので,
    初期の空間効率が圧倒的に悪い.
    Vlot は, vinit() で小さな {カード: 数} のテーブルを作るので,
    初期の空間効率が良い.

    Glot は, プレイヤー毎に配列の参照位置だけを持つため,
    プレイヤー毎の空間効率が良い.
    Vlot は, プレイヤー毎に vinit() で作ったテーブルの複製を持つため,
    プレイヤー毎の空間効率が悪い.

    Glot vs Vlot の空間効率は, プレイヤー数が増えるほど Glot が有利となる.
    しかし, 実測値を計っていないため, 損益分岐点がどこか不明.


Glot 同様に Redis が起動していれば ./manage.py shell で動作確認が可能.

>>> from glot import vinit, vget
>>> vinit('gacha1', [(1, 5), (2, 5), (1, 5), (2, 5)])
>>> [vget('gacha1') for x in xrange(0, 100)]

この例では, デッキの中に 1 と 2 のカードが 10 ずつ入る.

get() では, 引いたカードだけ取得できたが,
vget() では引いたカードとデッキの中を取得できる.

>>> (card_id, deck) = vget('gacha1')

この例であれば deck は,
{1: 10, 2: 10} ->..snip..-> {1: 0, 2: 1}
のように変化して行き, 最終的に全てのカードが尽きると None となる.

deck が None になった後, 更に vget() を行うと
再び vinit() で設定したデッキから複製が作成され,
その複製されたデッキからカードを引く.

Glot 同様にプレイヤー毎にデッキを用意する事も可能(これが主な使い方).
詳細は, 本ドキュメント内の関数の説明を参照の事.

Vlot では, デッキ内のカード枚数を自由に増減できる.

>>> from glot import vincr, vdecr
>>> vinit('gacha2', [(1, 5), (2, 5)]) # {1: 5, 2: 5}
>>> deck1 = vincr('gacha2', 2, 2)     # {1: 5, 2: 7}
>>> deck2 = vdecr('gacha2', 1, 2)     # {1: 3, 2: 7}

vincr() は, デッキに存在しないカードを指定されるとカードを追加するが,
vdecr() は, デッキに存在しないカードを指定されると例外が発生する.

---------------------
Django の設定について
---------------------

Django settings に下記を追加する事.

.. code-block:: python

   GLOT_SETTINGS = {
       'KEY_PREFIX': 'ApplicationName',
       'DB': 'glot', # see REDIS_DATABASES
       'USE_KVS_MODULE_CONNECTION': False,

       # Glot でのみ使用
       'TRY_INCREMENT_POSITION_COUNT': 10000,
       'POSITION_LIMIT': 9999999999,

       # Vlot でのみ使用
       'TRY_CLONE_COUNT': 10000,
       'TRY_GET_COUNT': 10000,
   }

   REDIS_DATABASES = {
       # ..snip..

       'glot': {
           'HOST': 'localhost',
           'PORT': '6379',
           'DB': '0',
       }

       # ..snip..
   }


KEY_PREFIX
    Redis に保存するキーの接頭辞を指定する.
    未指定の場合, Glot であれば 'Glot' を Vlot であれば 'ViewableGlot' を使用する.

DB
    settings.REDIS_DATABASES[settings.GLOT_SETTINGS['DB']] で使用する Redis
    サーバを決定している.
    settings.GLOT_SETTINGS や settings.REDIS_DATABASES が存在しない場合,
    localhost:6379 の db=0 に接続する.

USE_KVS_MODULE_CONNECTION
    True にすると, KVS モジュールのコネクションを利用する.
    KVS モジュールに渡す DB 名は, settings.GLOT_SETTINGS['DB'] を使用する.
    既に, KVS モジュールを利用しているのであれば,
    True にする事で Redis への接続数を押さえる事ができる.
    False であれば, Glot 内で Redis へ接続するため,
    スレッド毎に Redis へ接続する.

TRY_INCREMENT_POSITION_COUNT
    Glot でのみ使用され, Vlot では使用しなし.
    get() で使用する.
    配列の参照位置を不分割に増分する試行回数.
    get() に player_id を指定した場合, 増分に失敗する可能性が下がる.
    未指定の場合, 10000 を使用する.

POSITION_LIMIT
    Glot でのみ使用され, Vlot では使用しない.
    get() で使用する.
    プレイヤー毎にデッキを **作らない** 場合に使用される.
    配列の参照位置は, "カウンター % カードの総数" で算出している.
    しかし, 無限にカウンターを増分するわけにはいかないので,
    POSITION_LIMIT でカウンターの最大値を指定する.
    未指定の場合, 9999999999(nine ten) を使用する.

TRY_CLONE_COUNT
    Vlot でのみ使用され, Glot では使用しない.
    vclone() で使用する.
    デッキを不分割に複製する試行回数.

TRY_GET_COUNT
    Vlot でのみ使用され, Glot では使用しない.
    vget() で使用する.
    カードの残数を不分割に減算する試行回数.

------------
API 関数詳細
------------
"""
import threading

from glot import Glot
from viewable import ViewableGlot
from settings import Loader

_memoize_object = threading.local()

def _new(kind, client):
    obj = getattr(_memoize_object, kind, None)
    if obj is not None:
        return obj

    conf = Loader()

    if kind == 'glot':
        kwargs = conf.glot_kwargs(client)
        obj = Glot(**kwargs)
    else:
        kwargs = conf.vlot_kwargs(client)
        obj = ViewableGlot(**kwargs)

    setattr(_memoize_object, kind, obj)
    return obj

def init(deck_id, card_and_appearance, shard=1, client=None):
    """
    デッキを初期化する.
    必ず **get()** の前に実行する事.
    既に同一 ID のデッキが存在した場合, 上書きする.
    しかし, 前回の内容と変化が無ければ処理を行わない.
    既に存在するデッキの shard を変更する場合も **init** を使用する事.

    :param string deck_id: デッキの一意キー. 用途ごとにデッキを使い分ける事.
    :param card_and_appearance: カードと枚数のタプルをリストで指定. [(カードID, 枚数), ...]
    :param int shard: 指定された shard の数だけデッキを作成する. 同一 Redis にデッキを作成するので負荷分散ではない. カードの並び順が異なるデッキを作成し, プレイヤーを振り分ける事で予測を困難にする. しかし, プレイヤー毎にデッキの開始位置が異なるので, デッキが十分に大きければ shard=1 でも予測は困難である.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :type card_and_appearance: [(string, string), ...]
    :return: True .. 初期化, False .. 以前のデータと変化なし(未初期化)
    :raises: Glot.ShardValueError

    - Glot.ShardValueError -- shard は 1 以上の値を設定する事
    """
    return _new('glot', client).init(deck_id, card_and_appearance, shard)

def get(deck_id, player_id='common', client=None):
    """
    デッキからカードを引く.
    必ず **init()** の後に実行する事.

    :param string deck_id: デッキの一意キー.
    :param string player_id: プレイヤーの一意キー. 未指定時は、全プレイヤー共通のデッキが使用される.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: string -- card_id
    :raises: Glot.GetShardError, Glot.GetCardIDError, Glot.GetDeckLengthError, Glot.IncrementPositionError

    - Glot.GetShardError -- init 忘れか Redis 停止
    - Glot.GetCardIDError -- init 失敗か Redis 停止
    - Glot.GetDeckLengthError -- init 失敗か Redis 停止
    - Glot.IncrementPositionError -- 既定回数以上, 参照位置の更新に失敗
    """
    return _new('glot', client).get(deck_id, player_id)

def clean(deck_id, client=None):
    """
    デッキを削除する.
    デッキに付随するプレイヤー毎の参照位置も削除する.

    :param string deck_id: デッキの一意キー.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    """
    return _new('glot', client).clean(deck_id)

def vinit(deck_id, card_and_appearance, client=None):
    """
    デッキを初期化する.
    必ず **vinfo()/vget()** の前に実行する事.
    既に同一 ID のデッキが存在した場合, 上書きする.
 
    :param string deck_id: デッキの一意キー.
    :param card_and_appearance: カードと枚数のタプルをリストで指定. [(カードID, 枚数), ...]
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    """
    _new('vlot', client).init(deck_id, card_and_appearance)

def vclone(deck_id, player_id='common', client=None):
    """
    vinit() で作成したデッキをプレイヤー用に複製する.
    必ず **vinit()** の後に実行する事.
    vclone() の前に vget() が実行されると, vclone は自動的に行われる.
    そのため, このメソッドは,
    カードを引く前にデッキを作成する演出のためだけに存在する.

    :param string deck_id: デッキの一意キー.
    :param string player_id: プレイヤーの一意キー. 省略もできるが省略する意味がない.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: dict -- {カードID: カード残数, ...}
    :raises: ViewableGlot.GetDeckError, ViewableGlot.CloneError

    - Glot.GetDeckError -- vinit 忘れか Redis 停止
    - Glot.CloneError -- 既定回数以上, デッキの複製に失敗
    """
    return _new('vlot', client).clone(deck_id, player_id)

def vinfo(deck_id, player_id='common', client=None):
    """
    プレイヤー毎に複製されたデッキの状態を取得する.
    必ず **vinit()** の後に実行する事.
    vclone() 前であれば, vinit() で初期化した際のデッキ状態を返す.

    :param string deck_id: デッキの一意キー.
    :param string player_id: プレイヤーの一意キー. 省略もできるが省略する意味がない.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: dict -- {カードID: カード残数, ...}
    :raises: ViewableGlot.GetDeckError
 
    - Glot.GetDeckError -- vinit 忘れか Redis 停止
    """
    return _new('vlot', client).info(deck_id, player_id)

def vget(deck_id, player_id='common', client=None):
    """
    デッキからカードを引く.
    必ず **vinit()** の後に実行する事.
    vclone() 前であれば, vget() がデッキを自動複製する.

    :param string deck_id: デッキの一意キー.
    :param string player_id: プレイヤーの一意キー. 未指定時は、全プレイヤー共通のデッキが使用される.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: (string, {string, int}) -- (引いたカード, {カード: カード残数, ...})
    :raises: ViewableGlot.GetError, ViewableGlot.GetDeckError, ViewableGlot.LotError
 
    - ViewableGlot.GetError -- 既定回数以上, カードの取得に失敗
    - ViewableGlot.GetDeckError -- vinit 忘れか Redis 停止
    - ViewableGlot.LotError -- 確率計算の失敗. 絶対発生しない.
    """
    return _new('vlot', client).get(deck_id, player_id)

def vget_candidate(deck_id, player_id='common', client=None):
    """
    デッキからカードを引くが, 実際にはデッキから枚数を減算しない.

    :param string deck_id: デッキの一意キー.
    :param string player_id: プレイヤーの一意キー. 未指定時は、全プレイヤー共通のデッキが使用される.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: string -- 引いたカード(デッキから枚数を減算しない)
    :raises: ViewableGlot.GetError, ViewableGlot.GetDeckError, ViewableGlot.LotError
 
    - ViewableGlot.GetError -- 既定回数以上, カードの取得に失敗
    - ViewableGlot.GetDeckError -- vinit 忘れか Redis 停止
    - ViewableGlot.LotError -- 確率計算の失敗. 絶対発生しない.
    """
    return _new('vlot', client).get_candidate(deck_id, player_id)

def vdecr(deck_id, card_id, value, player_id='common', client=None):
    """
    指定したカードの枚数を減算する.

    :param string deck_id: デッキの一意キー.
    :param string card_id: 対象のカード
    :param int value: 減算数
    :param string player_id: プレイヤーの一意キー. 未指定時は、全プレイヤー共通のデッキが使用される.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: {string, int} -- {カード: カード残数, ...} 減算後のデッキ.
    :raises: ViewableGlot.GetError, ViewableGlot.GetDeckError, ViewableGlot.LotError
 
    - ViewableGlot.GetError -- 既定回数以上, カードの取得に失敗
    - ViewableGlot.GetDeckError -- vinit 忘れか Redis 停止
    - ViewableGlot.DoesNotCardIDError -- 対象のカードがデッキに存在しない
    - ViewableGlot.DecrError -- 減算した結果, 枚数が負の値となった
    """
    return _new('vlot', client).decr(deck_id, card_id, value, player_id)

def vincr(deck_id, card_id, value, player_id='common', client=None):
    """
    指定したカードの枚数を加算する.
    存在しないカードを指定すると, カードの追加となる.

    :param string deck_id: デッキの一意キー.
    :param string card_id: 対象のカード
    :param int value: 加算数
    :param string player_id: プレイヤーの一意キー. 未指定時は、全プレイヤー共通のデッキが使用される.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    :return: {string, int} -- {カード: カード残数, ...} 加算後のデッキ.
    :raises: ViewableGlot.GetError, ViewableGlot.GetDeckError, ViewableGlot.LotError
 
    - ViewableGlot.GetError -- 既定回数以上, カードの取得に失敗
    - ViewableGlot.GetDeckError -- vinit 忘れか Redis 停止
    """
    return _new('vlot', client).incr(deck_id, card_id, value, player_id)

def vclean(deck_id, client=None):
    """
    デッキを削除する.
    プレイヤー毎のデッキも削除する.

    :param string deck_id: デッキの一意キー.
    :param RedisClient client: Redis のクライアント. 渡さない場合は, glot 内で Redis にコネクションを張る.
    """
    return _new('vlot', client).clean(deck_id)
