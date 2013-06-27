# -*- coding: utf-8 -*-
"""
モデルを実装した後, モデルと組み合わせたガチャ処理の Mix-in クラスを実装する.

例えば, 幻獣姫であれば次の通り.

.. code-block:: python

    from ggacha.logic import ForegroundLogicMixin, BackgroundLogicMixin
    from module.gacha.impl.models import GenjuHimePlayerModelMixin

    class GenjuHimeForegroundLogicMixin(GenjuHimePlayerModelMixin,
                                        ForegroundLogicMixin):
        pass

    class GenjuHimeBackgroundLogicMixin(GenjuHimePlayerModelMixin,
                                        BackgroundLogicMixin):
        pass


pass 一行だが, これで幻獣姫用の Logic Mix-in クラスとなる.

これを /path/to/gacha/impl/logic.py 等に保存して使用する.

最後に, ガチャ毎のガチャ処理を実装する. 
例えば, 幻獣姫の無料(ポイント)ガチャであれば次の通り.

.. code-block:: python

    from module.playergashapon.api import acquire_gashapon_cards

    from module.gacha.impl.logic import GenjuHimeForegroundLogicMixin
    from module.gacha.models import Gacha
    from module.gacha.normal import GACHA_ID

    class PointLogicMixin(GenjuHimeForegroundLogicMixin):
        gacha_id = GACHA_ID

        def do_gacha(self, player):
            card_id = self.lottery.get(1) # deck_id = 1 を使う
            return acquire_gashapon_cards(player, [card_id], Gacha.get(gacha_id))


Mix-in するクラスを GenjuHimeForegroundLogicMixin から
GenjuHimeBackgroundLogicMixin に切り替えるだけで,
フォワグランド処理からバックグラウンド処理に切り替わるため,
状況に応じて使い分けが可能.

do_gacha の戻り値は, FinishView の finish メソッドに配送される.

do_gacha 内の lottery は, 後述のくじ引きを参照の事.
"""
from ggacha.utils import RaiseExceptionMixin, NullContext
from ggacha.conf import settings
from ggacha.session import SessionMixin
from ggacha.models import PlayerModelMixin
from ggacha.messaging import MessagingMixin
from ggacha.kvs import KVSMixin
from ggacha.lottery import LotteryMixin
from ggacha.worker import GachaWorkerMixin, DeadLetterGachaWorkerMixin
from ggacha.logging import LoggingMixin
from ggacha.logger import WritableLogMixin

class ForegroundLogicMixin(PlayerModelMixin,
                           SessionMixin, MessagingMixin, KVSMixin,
                           LotteryMixin, LoggingMixin,
                           RaiseExceptionMixin, WritableLogMixin):
    """
    ガチャの処理をフォアグラウンドで行う.
    主に無料のガチャ用.
    """
    def get_gacha_kwargs(self, request, *args, **kwargs):
        """
        このメソッドを上書きして do_gacha に渡す kwargs を返す.

        do_gacha() は, フォアグランドとバックグラウンドから実行されるため,
        request を受け取れない.

        そこで, このメソッドで do_gacha が受け取る kwargs を作成する.
        必ず, msgpack でシリアライズ可能な kwargs を返す事.

        :param HTTPRequest request: リクエストオブジェクト
        :return: do_gacha() に **kwargs として渡すディクショナリ
        """
        return {}

    def do_gacha(self, player, **kwargs):
        """
        このメソッドを上書きして, ガチャの処理を記述する事.

        バックグラウンド処理との整合性の都合で, 引数に request を受け取れない.

        必ず結果を返す事. 返された結果は, FinishView まで届く.

        :param object player: プレイヤーオブジェクト.
        :return: FinishView に渡す結果.
        :raises: NotImplementedError

        このメソッドを上書きしていない場合, NotImplementedError が発生する.
        """
        self.raise_not_impl('do_gacha')

    def logging_context(self, player, **kwargs):
        """
        ログ出力用のコンテキストを使用する場合のみ,
        このメソッドを上書きして, ログ出力用のコンテキストを返す事.

        :param object player: プレイヤーオブジェクト.
        :return: with で使用するログコンテキスト
        """
        return self.logging.get_null_context()

    def transaction_context(self, player, **kwargs):
        """
        View の check -> payment -> gacha
        をトランザクションで囲う際に上書きするメソッド.

        上書きしなければ, トランザクション無しで
        check -> payment -> gacha が実行される.

        gsc 内で horizontalpartitioning を使用するのであれば, 次の通り.

        .. code-block:: python

            from horizontalpartitioning import commit_on_success

            class EggLogicMixin(ForegroundLogicMixin):
                def transaction_context(self, player, **kwargs):
                    return commit_on_success([player.id])
        """
        return NullContext()

    def gacha(self, request, *args, **kwargs):
        """
        View から直接呼ばれるメソッド(上書き禁止).

        フォアグラウンドであるため, 即 do_gacha を実行する.
        """
        gacha_kwargs = self.get_gacha_kwargs(request, *args, **kwargs)
        self.write_log_debug(u'gacha: gacha_kwargs = %s', gacha_kwargs)
        with self.logging_context(self.player, **gacha_kwargs):
            self.write_log_debug(u'gacha: start do_gacha method')
            result = self.do_gacha(self.player, **gacha_kwargs)
            self.write_log_debug(u'gacha: end do_gacha method')
            self.write_log_debug(u'gacha: result = %s', result)
        self.kvs.set('session_result', {'status': 'foreground', 'result': result})
        self.kvs.set_result({'status': 'success', 'result': result})


class BackgroundLogicMixin(ForegroundLogicMixin, GachaWorkerMixin):
    """
    ガチャの処理をバックグラウンドで行う.

    有料のガチャや処理の重いガチャ用.

    View だけではなく, バックグラウンドプロセスからも Mix-in して使う.

    ForegroundLogicMixin クラスのサブクラスであるため do_gacha を持つ.
    """
    queue_name = None
    reply_queue_expires = 60 * 60 * 1000 # 1時間に設定(単位は ms)

    use_dead_letter = True
    message_expires = 12 * 60 * 60 * 1000 # 12時間

    @property
    def _queue_name(self):
        prefix = settings.QUEUE_NAME_PREFIX
        if not prefix:
            return self.queue_name
        return prefix + '_' + self.queue_name

    def gacha(self, request, *args, **kwargs):
        """
        View から直接呼ばれるメソッド(上書き禁止).

        do_gacha を処理せず, バックグランドへ処理依頼をするだけ.

        ただし, settings.GGACHA_SETTINGS['BACKGROUND_OFF'] = True であれば,
        フォアグラウンドで実行される.
        """
        self.raise_if_none('queue_name')
        if settings.BACKGROUND_OFF:
            self.write_log_debug(u'gacha: BACKGROUND_OFF')
            super(BackgroundLogicMixin, self).gacha(request, *args, **kwargs)
            return

        gacha_kwargs = self.get_gacha_kwargs(request, *args, **kwargs)
        self.write_log_debug(u'gacha: gacha_kwargs = %s', gacha_kwargs)
        with self.logging_context(self.player, **gacha_kwargs):
            logging_kwargs = self.logging.get_args(request)
            self.write_log_debug(u'gacha: logging_kwargs = %s', logging_kwargs)
            with self.messaging.connect() as connection:
                self.write_log_debug(u'gacha: Connect to MQ')
                queue_name = self._publish_to_worker(connection,
                                                     gacha_kwargs,
                                                     logging_kwargs)

        #TODO: 後で整形
        #self.session.set_background_result(queue_name)
        self.kvs.set('session_result', {'status': 'background',
                                        'result': queue_name})

    def _publish_to_worker(self, connection, gacha_kwargs, logging_kwargs):
        """
        返信用の Queue を作ってからバックグラウンドへ処理を依頼.
        返信用の Queue は, メッセージが 0 になるか時間切れで自動削除される.
        """
        queue_args = {'x-expires': self.reply_queue_expires}
        self.write_log_debug(u'_publish_to_worker: queue_args = %s',
                             queue_args)

        reply_queue = self.messaging.declare_queue(connection,
                                                   queue_arguments=queue_args)
        self.write_log_debug(u'_publish_to_worker: reply_queue = %s',
                             reply_queue.name)

        self.write_log_debug(u'_publish_to_worker: publish to %s',
                             self._queue_name)
        self.messaging.publish(connection,
                               {
                                   'player_id': self.player.pk,
                                   'gacha_kwargs': gacha_kwargs,
                                   'logging_kwargs': logging_kwargs,
                               },
                               routing_key=self._queue_name,
                               reply_to=reply_queue.name,)
        return reply_queue.name

    def start_worker(self):
        """
        バックグラウンド処理から呼ばれるメソッド.(上書き禁止)

        インナークラス GachaWorker を作って実行する.

        do_gacha は, GachaWorker の中で実行される.
        """
        if getattr(self, '_gacha_worker', None):
            self.stop_worker()

        queue_args = {
            'x-message-ttl': self.message_expires,
            'x-dead-letter-exchange' : '',
            'x-dead-letter-routing-key': 'dead_letter',
        } if self.use_dead_letter else {}

        with self.messaging.connect() as connection:
            queue = self.messaging.declare_queue(connection,
                                                 name=self._queue_name,
                                                 durable=True,
                                                 queue_arguments=queue_args)
        self.run_worker(queue)


class DeadLetterLogicMixin(BackgroundLogicMixin, DeadLetterGachaWorkerMixin):
    """
    Dead Letter を監視するロジック
    """
    queue_name = 'dead_letter'
    use_dead_letter = False # Dead Letter 本体であるため False
