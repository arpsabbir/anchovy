# -*- coding: utf-8 -*-
"""
ggacha.logic 配下のクラスに, くじ引き機能を提供する.
"""

from __future__ import absolute_import

import glot

from ggacha.redis import HasRedisClientMixin

class LotteryMixin(object):
    """
    くじ引きを行う機能を追加する Mix-in クラス.

    現在は glot 専用.
    将来的に異なるくじ引きモジュールに切り替える際,
    この Mix-in クラスだけ修正する予定.

    glot の Redis コネクションと, ggacha.kvs の Redis コネクションを
    共通化するため, 接続情報は ggacha.kvs と同じく
    settings.GGACHA_SETTINGS['REDIS_DB'] を使用する.

    .. note::

        gredis, submodules.kvs の順で Redis 接続を取得する.

    .. method:: lottry.init

        初期化処理を行う(くじ引きの箱にくじを詰め込む).
        主に DB に登録されている Master データの初期化と共に使用する.

        幻獣姫における manage.py のコマンドで初期化する例は次の通り.
        
        .. code-block:: python

            from django.core.management.base import NoArgsCommand
            from ggacha.lottery import LotteryMixin
            from module.gacha.models import GachaDeck

            class Command(LotteryMixin, NoArgsCommand):
                help = u'ガチャのカード出現数を更新します'

                def handle_noargs(self, **options):
                    print u"カード出現数 更新開始"
                    for deck in GachaDeck.get_all():
                        print "[", deck.name, "] now updating...",
                        result = self.lottery.init(deck.id, deck.glot_arg)
                        print "finish" if result is True else "pass"
                    print u"カード出現数 更新終了"


        このメソッドは, 実質, glot.init に
        Redis のコネクションを渡すラッパーであるため,
        引数/戻り値等の仕様は, glot のマニュアルを参照の事.
        

    .. method:: lottry.get

        くじを引く.
        LotteryMixin は, ggacha.logic 配下のクラスに Mix-in 済みであるため,
        ggacha.logic 配下のクラスは, self.lottry.get で, くじを引ける.

        このメソッドは, 実質, glot.get に
        Redis のコネクションを渡すラッパーであるため,
        引数/戻り値等の仕様は, glot のマニュアルを参照の事.
    """
    class _Lottery(HasRedisClientMixin):
        def init(self, *args, **kwargs):
            return glot.init(client=self.redis, *args, **kwargs)

        def get(self, *args, **kwargs):
            return glot.get(client=self.redis, *args, **kwargs)


    @property
    def lottery(self):
        if hasattr(self, '_lottery'):
            return self._lottery

        self._lottery = self._Lottery()
        return self._lottery


    class _VLottery(HasRedisClientMixin):
        def init(self, *args, **kwargs):
            return glot.vinit(client=self.redis, *args, **kwargs)

        def info(self, *args, **kwargs):
            return glot.vinfo(client=self.redis, *args, **kwargs)

        def clone(self, *args, **kwargs):
            return glot.vclone(client=self.redis, *args, **kwargs)

        def get(self, *args, **kwargs):
            return glot.vget(client=self.redis, *args, **kwargs)

        def get_candidate(self, *args, **kwargs):
            return glot.vget_candidate(client=self.redis, *args, **kwargs)

        def incr(self, *args, **kwargs):
            return glot.vincr(client=self.redis, *args, **kwargs)

        def decr(self, *args, **kwargs):
            return glot.vdecr(client=self.redis, *args, **kwargs)


    @property
    def vlottery(self):
        if hasattr(self, '_vlottery'):
            return self._vlottery

        self._vlottery = self._VLottery()
        return self._vlottery
