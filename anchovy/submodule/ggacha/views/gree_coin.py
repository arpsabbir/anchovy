# -*- coding: utf-8 -*-
"""
GREE コインのコールバック用 View を作成する.

Logic クラスや他の View クラスと同様に Player モデルに依存しているため,
抽象クラス PlayerModelMixin を継承した,
ゲーム毎の実装クラスを作成する必要がある. 

例えば, 幻獣姫であれば次の通り.

.. code-block:: python

    from ggacha.views.gree_coin import CallbackView
    from module.gacha.impl.models import GenjuHimePlayerModelMixin

    class GenjuHimeCallbackView(GenjuHimePlayerModelMixin, CallbackView):
        pass


これを /path/to/gacha/impl/views/gree_coin.py 等に保存して使用する.
"""
import time
import sys
import traceback

from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest

from gsocial import Payment
from gsocial.models import PaymentInfo
from gsocial.http import HttpResponseOpensocialRedirect

from ggacha.views.base import BaseView


class RedirectPathError(Exception):
    pass


class CallbackView(BaseView):
    """
    この View を継承して GREE からのコールバックを受ける View クラスを作る.

    例えば, 幻獣姫の有料ガチャのコールバックであれば次の通り.

    .. code-block:: python

        class GoldenCallbackView(GoldenLogicMixin, GenjuHimeCallbackView):
            pass


    ガチャ処理(Logic クラス)を Mix-in し, CallbackView を継承する.

    CallbackView に必要なプロパティは存在しないため, pass で良い.
    """
    class _TimeoutError(Exception):
        pass


    class _CheckError(Exception):
        pass


    def check(self, request, *args, **kwargs):
        """
        ガチャを行か判定を行う.

        上書きされなければ何も行われない.
        False を返すと, GREE に決済失敗を返す.
        デバック時, このメソッドは無視される.

        回数制限や回数毎に価格が変動するガチャは,
        このメソッドでの制限を怠ると, GREE の決済画面を何枚も開かれ,
        不正利用されるため, 絶対にこのメソッドを上書きする事.

        ここで重い処理を行うと, カードは追加されるが, 課金が無効となる.
        """
        return True

    def gacha(self, request, *args, **kwargs):
        """
        ガチャを行う.

        ggacha.logic 配下の Logic クラスを Mix-in すると上書きされるメソッド.
        直接上書きしない事.
        """
        self.raise_not_impl('gacha')

    def process(self, request, *args, **kwargs):
        """
        親である BaseView の process メソッドを上書き, ガチャの処理を行う.

        上書きしない事.
        """
        # 本来は GREE からコールされるべきだが
        # ローカルデバックで, 直接ブラウザからコールされている
        if settings.OPENSOCIAL_DEBUG:
            self.write_log_debug(u'process: OPENSOCIAL_DEBUG is True')
            return self._debug_callback(request, *args, **kwargs)

        # GREE からコールされた場合の処理
        return self._callback(request, *args, **kwargs)

    def _debug_callback(self, request, *args, **kwargs):
        # mixins.views.payment.GreeCoinMixin でデバック時のみ
        # session に gree_coin_redirect_path が設定される
        redirect_path = self.session.get('gree_coin_redirect_path')
        if not redirect_path:
            self.write_log_error(u'_debug_callback: redirect_path is None')
            raise RedirectPathError('gree_coin_redirect_path not found')

        gacha_kwargs = self.get_gacha_kwargs(request, *args, **kwargs)
        with self.transaction_context(self.player, **gacha_kwargs):
            result = self.check(request, *args, **kwargs)
            # gacha() を transaction に入れられない理由は,
            # _callback() 内のコメント参照の事. Kombu が悪い.

        if not result:
            self.write_log_debug(u'_debug_callback: check is False')
            self.kvs.set('session_result', {'status': 'disable'})
        else:
            with self.transaction_context(self.player, **gacha_kwargs):
                self.write_log_debug(u'_debug_callback: start gacha method')
                self.gacha(request, *args, **kwargs)
                self.write_log_debug(u'_debug_callback: end gacha method')

        self.write_log_debug(u'_debug_callback: redirect to %s', redirect_path)
        return HttpResponseOpensocialRedirect(redirect_path)

    def _callback(self, request, *args, **kwargs):
        start_time = int(time.time() * 1000)

        payment = Payment(request)
        payment_id = request.REQUEST.get('paymentId', None)
        payment_info = PaymentInfo.get_by_point_code(payment_id)

        self.write_log_debug(u'_callback: payment_id = %s', payment_id)
        self.write_log_debug(u'_callback: payment_info = %s', payment_info)

        if payment.is_success():
            self.write_log_debug(u'_callback: payment is success')
            gacha_kwargs = self.get_gacha_kwargs(request, *args, **kwargs)
            try:
                with self.transaction_context(self.player, **gacha_kwargs):
                    if not self.check(request, *args, **kwargs):
                        raise self._CheckError

                    # Kombu が AMQP tx に未対応であるため,
                    # Timeout か DeadLock が発生すると
                    # Background ではメッセージが飛んでしまう.
                    # よって, 暫くここはコメントアウトしとく.
                    #self.write_log_debug(u'_callback: start gacha method')
                    #self.gacha(request, *args, **kwargs)
                    #self.write_log_debug(u'_callback: end gacha method')

                    end_time = int(time.time() * 1000)
                    if end_time - start_time > 4000:
                        raise self._TimeoutError

                # Kombu が AMQP tx を使えないため,
                # 苦肉の策で, gacha() を transaction の外に出す.
                # Foregrand は諦める.
                with self.transaction_context(self.player, **gacha_kwargs):
                    self.write_log_debug(u'_callback: start gacha method')
                    self.gacha(request, *args, **kwargs)
                    self.write_log_debug(u'_callback: end gacha method')

            except self._CheckError:
                self.write_log_debug(u'_callback: check is False')
                self.kvs.set('session_result', {'status': 'disable'})
            except self._TimeoutError:
                self.write_log_error(u'_callback: TimeoutError %sms',
                                     end_time - start_time)
                self.kvs.set('session_result', {'status': 'error'})
            except:
                traceback.print_exception(file=sys.stdout, *sys.exc_info())
                self.write_log_except()
                self.kvs.set('session_result', {'status': 'error'})
            else:
                payment_info.save_as_succeeded()
                self.write_log_debug(u'_callback: return OK')
                return HttpResponse('OK', mimetype='text/plain')
        else:
            self.write_log_debug(u'_callback: payment is cancel')
            self.kvs.set('session_result', {'status': 'cancel'})

        payment_info.save_as_canceled()
        self.write_log_debug(u'_callback: return NG')
        return HttpResponseBadRequest('NG', mimetype='text/plain')
