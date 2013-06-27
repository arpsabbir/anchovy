# -*- coding: utf-8 -*-
"""
Logic クラスと同様に View クラスも Player モデルに依存しているため,
初めに抽象クラス PlayerModelMixin を継承した,
ゲーム毎の実装クラスを作成する必要がある.

例えば, 幻獣姫であれば次の通り.

.. code-block:: python

    from ggacha.views.base import BaseView, GachaView, FinishView
    from module.gacha.impl.models import GenjuHimePlayerModelMixin

    class GenjuHimeBaseView(GenjuHimePlayerModelMixin, BaseView):
        pass

    class GenjuHimeGachaView(GenjuHimePlayerModelMixin, GachaView):
        pass

    class GenjuHimeFinishView(GenjuHimePlayerModelMixin, FinishView):
        pass


これを /path/to/gacha/impl/views/base.py 等に保存して使用する.
"""
from django.http import HttpResponse
from django.views.generic.base import View

from gsocial.http import HttpResponseOpensocialRedirect

from ggacha.utils import RaiseExceptionMixin
from ggacha.session import SessionMixin
from ggacha.models import PlayerModelMixin
from ggacha.messaging import MessagingMixin
from ggacha.kvs import KVSMixin
from ggacha.logger import WritableLogMixin


class BaseView(PlayerModelMixin,
               SessionMixin, MessagingMixin, KVSMixin,
               RaiseExceptionMixin, WritableLogMixin,
               View):
    """
    GachaView や FinishView の元となる View クラス.

    GachaView や FinishView 以外の View クラス(例えば結果画面など) を
    作成する際に, この View クラスを継承して View クラスを作る.

    例えば, 幻獣姫の無料(ポイント)ガチャの結果ページであれば次の通り.
    (ただし, 結果ページは ResultView クラスを使用する事)

    .. code-block:: python

        class XanaduResultView(TemplateResponseMixin, GenjuHimeBaseView):
            gacha_id = GACHA_ID
            template_name = 'gacha/zanadu/result.html'

            def process(self, request, *args, **kwargs):
                return self.render_to_response({
                    'result' :  self.kvs.get_result()
                })


    GET か POST メソッドでアクセスされた場合, process が呼ばれる.
    FinishView が呼ばれた後であれば, self.kvs.get_result() で
    Logic クラスの do_gacha の結果を取り出す事ができる.

    結果は, ガチャ毎/ユーザ毎に一意であるため,
    self.kvs.get_result() で取得できる結果は,
    常に「このガチャの このユーザの 前回の結果」となる.

    この仕様のため, 同じガチャを行うと結果が上書きされる.
    """

    def init(self, request, *args, **kwargs):
        """
        上書きして, request を使用した初期化処理を記述する.

        Mix-in で上書きされなければ何も行われない.
        HttpResponse を継承したインスタンスを返すと,
        続く process メソッドは実行されない.
        """
        return True

    def process(self, request, *args, **kwargs):
        """
        上書きしてリクエスト処理を記述する.

        :param HTTPRequest request: リクエスト
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        引数は request 以外に urls.py から args と kwargs を受け取る.

        このメソッドを上書きしていない場合, NotImplementedError が発生する.
        """
        self.raise_not_impl('process')

    def get(self, request, *args, **kwargs):
        self.init_player(request)

        response = self.init(request, *args, **kwargs)
        if isinstance(response, HttpResponse):
            return response

        self.init_session(request, self.gacha_id, self.player.pk)
        self.init_kvs(self.gacha_id, self.player.pk)

        return self.process(request, *args, **kwargs)

    post = get


class GachaView(BaseView):
    """
    ガチャを引くための View クラス.

    この View を継承してガチャを引く View クラスを作る.

    例えば, 幻獣姫の無料(ポイント)ガチャの結果ページであれば次の通り.

    .. code-block:: python

        class XanaduView(GenjuHimePointMixin, XanaduLogicMixin, GenjuHimeGachaView):
            need_amount = AMOUNT
            # 他の View とは異なり
            # Mix-in した Logic クラスで既に gacha_id が設定さているため
            # gacha_id の設定を省いている

            def __init__(self, **kwargs):
                super(PointView, self).__init__(**kwargs)
                self.redirect_path = reverse('mobile_gacha_xanadu_finish')


    課金処理(Payment クラス)、ガチャ処理(Logic クラス)を Mix-in し, 
    GachaView を継承する.

    GachaView を継承すると, redirect_path プロパティの上書きが必須となる.
    reverse() を使う場合, urls.py の評価が終わっている必要があるので,
    class オブジェクトの生成時ではなく, object オブジェクトの生成時である
    __init__ で設定を行う.

    .. note::

        Python では仕様上, クラスとトレイトは明確に区別されていない.

        しかし, Mix-in するのは 'has a' の関係であり,
        継承するのは 'is a' の関係であるべき.

        これを意識せずに多重継承を用いると,
        コードが複雑になり, バグの温床になる.

        また, C3 アルゴリズムを正しく理解する事も必須である.
    """

    redirect_path = None # Mix-in した際に必ず初期化する事

    def check(self, request, *args, **kwargs):
        """
        ガチャを行か判定を行う.

        例えば, ガチャが期間外等の判定を行う.

        Mix-in で上書きされなければ何も行われない.
        HttpResponse を継承したインスタンスを返すと,
        続く payment メソッドと gacha メソッドは実行されない.

        payment メソッドの中でも, ガチャを続行するか否か判定できるが
        payment メソッド内では課金に関する確認だけを行う事.

        逆に, このメソッド内でポイント不足等の課金に関する判定は行わない事.
        """
        return True

    def payment(self, request, *args, **kwargs):
        """
        課金を行う.

        ggacha.view.payment 配下の Payment クラスを
        Mix-in すると上書きされるメソッド.
        直接上書きしない事.
        """
        self.raise_not_impl('payment')

    def gacha(self, request, *args, **kwargs):
        """
        ガチャを行う.

        ggacha.logic 配下の Logic クラスを Mix-in すると上書きされるメソッド.
        直接上書きしない事.
        """
        self.raise_not_impl('gacha')

    def process(self, request, *args, **kwargs):
        """
        親である BaseView の process メソッドを上書き
        check -> payment -> gacha の順にメソッドを実行する.

        上書きしない事.

        .. note::

            もし, gacha の後ろに失敗する可能性のある別の処理を配置するならば,
            実体である BackgroundLogicMixin の gacha メソッドは,
            MQ の publish をトランザクション内で実行する必要がある.

            現在, gacha の後ろに失敗する処理はないため, 考慮しなくとも良い.

            AMQP は Publish をトランザクション内に含める事ができるため,
            必要があれば, トランザクションを使用する事.
        """
        self.raise_if_none('redirect_path')

        # 以前の結果を削除
        #self.session.delete_result()
        #TODO: 後で整形
        self.kvs.delete('session_result')
        self.kvs.delete_result()

        gacha_kwargs = self.get_gacha_kwargs(request, *args, **kwargs)
        with self.transaction_context(self.player, **gacha_kwargs):
            for process in [self.check, self.payment]:
                response = process(request, *args, **kwargs)
                if isinstance(response, HttpResponse):
                    return response

            self.gacha(request, *args, **kwargs)
            return HttpResponseOpensocialRedirect(self.redirect_path)


class FinishView(BaseView):
    """
    GachaView(と Logic)が終わるのを待つ View クラス.

    例えば, 幻獣姫の無料(ポイント)ガチャの終了ページであれば次の通り.

    .. code-block:: python

        class XanaduFinishView(TemplateResponseMixin, GenjuHimeFinishView):
            gacha_id = GACHA_ID
            template_name = 'gacha/xanadu/failure.html'

            def finish(self, request, result, *args, **kwargs):
                # FLASH マッピング処理
                # フラッシュの表示処理

            def failure(self, request, *args, **kwargs):
                return self.render_to_response({})


    Logic クラスの do_gacha メソッドの結果が
    finish メソッドの result に設定される.

    ただし, バックグラウンドで実装された do_gacha が
    4 秒待っても終わらない場合, finish メソッドの代わりに
    failure メソッドが呼ばれる.
    """

    class _ChannelError(object):
        pass


    def finish(self, request, result, *args, **kwargs):
        """
        上書きして最終処理を記述する.

        :param HTTPRequest request: リクエスト
        :param object result: Logic クラス do_gacha メソッドの戻り値
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        do_gacha の結果が取得できない場合, finish は実行されず,
        failure が実行される.

        FinishView は, 何度リロードされても result に毎回同じ結果が入るため,
        カード枚数が多く, FLASH の分割表示が必要な場合であっても,
        引数に表示位置を追加する等で対処できる.

        幻獣姫の 6 連ガチャであれば次の通り. 

        .. code-block:: python

            # urls.py
            urlpatterns += patterns('',
                url(r'golden6/finish/(?P<count>\d)/$',
                    Golden6FinishView.as_view(),
                    name='mobile_gacha_golden6_finish')
            )

            # views.py
            class Golden6View(GenjuHimeGreeCoinMixin, GenjuHimeGachaView):
                # ..snip..
                def __init__(self, **kwargs):
                    # ..snip..
                    self.redirect_path = reverse('mobile_gacha_golden6_finish',
                                                 kwargs={'count': 0})

            class Golded6FinishView(TemplateResponseMixin, GenjuHimeFinishView):
                # ..snip..
                def finish(self, request, result, count=0, *args, **kwargs):
                    # ..snip..
                    count = int(count)
                    separete_length = 5
                    offset = separete_length * count
                    over_length = cards_length - offset
                    if over_length <= separete_length:
                        next_url = reverse('mobile_gacha_golden6_result')
                    else:
                        next_url = reverse('mobile_gacha_golden6_finish',
                                           kwargs={'count': count + 1})
                    # ..snip..
        """
        self.raise_not_impl('finish')

    def failure(self, request, *args, **kwargs):
        """
        上書きしてエラー処理を記述する.

        :param HTTPRequest request: リクエスト
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        バックグラウンドのエラー,
        ユーザがキャンセルを押した,
        キューの名前を取得できない場合,
        finish のかわりに実行される.

        タイムアウト時, timeout を定義していない場合も, こちらが実行される.
        """
        self.raise_not_impl('failure')

    def cancel(self, request, *args, **kwargs):
        """
        上書きしてキャンセル時の処理を記述する.

        :param HTTPRequest request: リクエスト
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        キャンセルされた場合, こちらが実行される.
        定義していない場合, failure を実行する.

        ガチャTOP等にリダイレクトすると良い.
        """
        return self.failure(request, *args, **kwargs)

    def disable(self, request, *args, **kwargs):
        """
        上書きして callback の check メソッドが
        False を返した時の処理を記述する.

        :param HTTPRequest request: リクエスト
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        定義していない場合, failure を実行する.
        """
        return self.failure(request, *args, **kwargs)

    def timeout(self, request, *args, **kwargs):
        """
        上書きしてタイムアウト時の処理を記述する.

        :param HTTPRequest request: リクエスト
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        do_gacha の結果が取得できない場合, こちらが実行される.
        定義していない場合, failure を実行する.

        基本的には, ブラウザの再読み込みを促すメッセージを表示しておく.
        念のため, ガチャTOP等のリンクも画面に表示しておくと良い.
        """
        return self.failure(request, *args, **kwargs)

    def process(self, request, *args, **kwargs):
        """
        親である BaseView の process メソッドを上書き
        KVS -> MQ -> KVS の順に
        do_gacha メソッドの結果が届いていないか確認を行い,
        finish, failure, cancel, disable, timeout メソッドを呼び分ける.

        上書きしない事.
        """
        result = self.kvs.get('session_result')
        self.write_log_debug(u'process: result = %s', result)

        if not isinstance(result, dict):
            self.write_log_debug(u'process: result is not dict')
            return self.failure(request, *args, **kwargs)

        # エラー
        if result.get('status', 'error') == 'error':
            self.write_log_debug(u'process: result.status is error')
            return self.failure(request, *args, **kwargs)

        # キャンセル
        if result['status'] == 'cancel':
            self.write_log_debug(u'process: result.status is cancel')
            return self.cancel(request, *args, **kwargs)

        # 無効(callback の check メソッドで False を返した)
        if result['status'] == 'disable':
            self.write_log_debug(u'process: result.status is disable')
            return self.disable(request, *args, **kwargs)

        # フォアグラウンドなら即終了
        if result['status'] == 'foreground':
            self.write_log_debug(u'process: result.status is foreground')
            return self.finish(request, result['result'], *args, **kwargs)

        # 結果 Queue の名前を取得
        self._reply_to = result.get('result', None)
        self.write_log_debug(u'process: reply_to = %s', self._reply_to)
        if self._reply_to is None:
            self.write_log_debug(u'process: reply_to is None')
            return self.failure(request, *args, **kwargs)

        # MQ から結果取得
        with self.messaging.connect() as connection:
            self.write_log_debug(u'process: Connect to MQ')
            try:
                with self.messaging.consume(
                    connection, self._reply_to
                ) as (body, message):
                    self.write_log_debug(u'process: body = %s, msg = %s',
                                         body, message)
                    if None in [body, message]:
                        background_result = self._ChannelError()
                    else:
                        background_result = body
            except: # AMQPChannelException (Timeout or Queue が存在しない)
                self.write_log_except()
                background_result = self._ChannelError()

            if not isinstance(background_result, self._ChannelError):
                self.messaging.delete_queue(connection, self._reply_to)

        # MQ から結果を取得できた
        if not isinstance(background_result, self._ChannelError):
            self.write_log_debug(u'process: background_result = %s',
                                 background_result)
            return self._finish_or_failure(request, background_result,
                                           *args, **kwargs)

        result_on_kvs = self.kvs.get_result()
        self.write_log_debug(u'process: result_on_kvs = %s', result_on_kvs)
        # KVS 結果を取得(複数端末 and リロード対策)
        if result_on_kvs is not None:
            self.write_log_debug(u'process: result_on_kvs is not None')
            return self._finish_or_failure(request, result_on_kvs,
                                           *args, **kwargs)

        # 全ての試行に失敗した
        self.write_log_debug(u'process: timeout')
        return self.timeout(request, *args, **kwargs)

    def _finish_or_failure(self, request, result, *args, **kwargs):
        if not isinstance(result, dict):
            self.write_log_debug(u'_finish_or_failure: result is not dict')
            return self.failure(request, *args, **kwargs)

        if result.get('status', None) != 'success':
            self.write_log_debug(
                u'_finish_or_failure: result.status is not success')
            return self.failure(request, *args, **kwargs)

        self.write_log_debug(u'_finish_or_failure: finish!')
        return self.finish(request, result['result'], *args, **kwargs)


class ResultView(BaseView):
    """
    FinishView の後に結果等を表示する View クラス.

    .. code-block:: python

        class XanaduResultView(TemplateResponseMixin, GenjuHimeResultView):
            gacha_id = GACHA_ID
            template_name = 'gacha/zanadu/result.html'

            # result は, FinishView.finish の引数と同値
            def success(self, result, *args, **kwargs):
                return self.render_to_response({
                    'result': result
                })

            def failure(self, request, *args, **kwargs):
                raise


    Logic クラスの do_gacha メソッドの結果が
    success メソッドの result に設定される.

    result が存在しない場合, success メソッドの代わりに
    failure メソッドが呼ばれる.
 
    FinishView の様に, 結果を待つ事がないため,
    必ず FinishView の後に使用する事.
    """
    def success(self, request, result, *args, **kwargs):
        """
        上書きして結果を使用した処理を記述する.

        :param HTTPRequest request: リクエスト
        :param object result: Logic クラス do_gacha メソッドの戻り値
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        do_gacha の結果が取得できない場合, success は実行されず,
        failure が実行される.
        """
        self.raise_not_impl('success')

    def failure(self, request, *args, **kwargs):
        """
        上書きしてエラー処理を記述する.

        :param HTTPRequest request: リクエスト
        :return: HttpResponse オブジェクト
        :raises: NotImplementedError

        do_gacha の結果が取得できない場合, success のかわりに実行される.
        """
        self.raise_not_impl('failure')

    def process(self, request, *args, **kwargs):
        """
        親である BaseView の process メソッドを上書き
        do_gacha メソッドの結果が届いていないか KVS を確認し,
        success メソッドと failure メソッドを呼び分ける.

        上書きしない事.
        """
        result_on_kvs = self.kvs.get_result()
        self.write_log_debug(u'process: result_on_kvs = %s', result_on_kvs)
        if result_on_kvs is None:
            self.write_log_debug(u'process: result_on_kvs is None')
            return self.failure(request, *args, **kwargs)
        self.write_log_debug(u'process: success!')
        return self.success(request, result_on_kvs['result'], *args, **kwargs)
