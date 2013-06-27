# -*- coding: utf-8 -*-
"""
モデルと組み合わせた課金処理の Mix-in クラスを実装する.

例えば, 幻獣姫であれば次の通り.

初めに import から.

.. code-block:: python

    from ggacha.utils import HasGachaIDMixin
    from ggacha.views.payment import PaymentMixin, FreeParOneDayMixin, GreeCoinMixin

    from module.common.middleware.error_page import ErrorPageException
    from module.playergashapon.api import get_player_gashapon_ticket

    from module.gacha.impl.models import GenjuHimePlayerModelMixin


一日一回無料 二回以降からポイント消費する課金処理の例.

.. code-block:: python

    class GenjuHimePointMixin(GenjuHimePlayerModelMixin, FreeParOneDayMixin):
        def decrement_amount(self, amount):
            if self.player.point < amount:
                raise ErrorPageException('GACHA_ERROR.PAYMENT_POINT')

            self.player.sub_point(amount)
            self.player.save()
            return True


decrement_amount メソッドを上書きしてポイント減算処理を記述する.

PlayerModelMixin の実装である GsweetsPlayerModelMixin を
Mix-in しておかないと self.player が使えない.

減算成功なら True を, 減算失敗なら HttpResponse を返すか raise する.


次にチケットを消費する課金処理の例.

.. code-block:: python

    class GenjuHimeTicketMixin(GenjuHimePlayerModelMixin, HasGachaIDMixin, PaymentMixin):
        def decrement_amount(self, amount):
            ticket = get_player_gashapon_ticket(self.player, self.get_gacha_id())
            if not ticket or ticket.number < amount:
                raise ErrorPageException('GACHA_ERROR.PAYMENT_TICKET')

            ticket.number -= amount
            ticket.save()
            return True


HasGachaIDMixin を Mix-in しておかないと, self.get_gacha_id() が使えない.


最後に GREE コインを消費する課金処理の例.

.. code-block:: python

    class GenjuHimeGreeCoinMixin(GreeCoinMixin):
        pass


実は, GreeCoinMixin に実装は必要ない.
他の課金処理と合わせるため, 幻獣姫用のクラスを用意しておく.

これを /path/to/gacha/impl/views/payment.py 等に保存して使用する.
"""

from datetime import datetime

from django.conf import settings
from django.http import HttpResponseRedirect

from gsocial.utils.payment import Payment
from gsocial.models import get_osuser
from gsocial.http import HttpResponseOpensocialRedirect

from ggacha.utils import RaiseExceptionMixin, HasGachaIDMixin, NullContext
from ggacha.models import PlayerModelMixin
from ggacha.kvs import KVSMixin
from ggacha.logger import WritableLogMixin


class PaymentMixin(PlayerModelMixin, RaiseExceptionMixin):
    """
    課金処理の元となる課金クラス.

    全ての課金トレイトで need_amount を初期化する事.
    """

    need_amount = None

    def get_amount(self, request, *args, **kwargs):
        """
        消費ポイントの変動を need_amount の初期化で対応できない場合,
        このメソッドを上書きする.
        """
        self.raise_if_none('need_amount')
        return self.need_amount

    def decrement_amount(self, amount):
        """
        このメソッドを上書きしてポイント減算処理を記述する.

        減算に成功した場合, True を返す.

        失敗した場合, raise するか HttpResponse を継承したインスタンスを返す.

        self.player でプレイヤーモデルにアクセス可能.
        """
        self.raise_not_impl('decrement_amount')

    def payment(self, request, *args, **kwargs):
        """
        View クラスから直接呼ばれるメソッド(上書き禁止).

        get_amount -> decrement_amount の順にメソッドを実行する.

        quantity は使用しない. 例えば "10連ガチャ" なら,
        need_amount にボリュームディスカウントを考慮したポイントを設定しておく.
        """
        amount = self.get_amount(request, *args, **kwargs)
        return self.decrement_amount(amount)


class FreeParOneDayMixin(PaymentMixin, KVSMixin):
    """
    一日一回無料の課金クラス.
    """

    def get_amount(self, request, *args, **kwargs):
        """
        一日一回無料にする.(上書き禁止)

        有料時は, need_amount に設定された値を使う.
        """
        self.raise_if_none('need_amount')

        # KVSMixin の get_last_gacha_datetime は, ガチャ毎/プレイヤー毎に一意.
        last_datetime = self.kvs.get_last_gacha_datetime()
        if last_datetime is None:  # 初めて
            return 0

        def _trim_time(dt):
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)

        last_date = _trim_time(last_datetime)
        today = _trim_time(datetime.now())
        if last_date < today:  # 日付が変わっている
            return 0

        return self.need_amount


class GreeCoinMixin(HasGachaIDMixin, PaymentMixin, WritableLogMixin):
    """
    GREEコインを消費する課金クラス.

    item_id_base, item_name, item_description,
    media_path, callback_path, finish_path を初期化する事.

    GREE に送信される item_id は, gacha.id + item_id_base となる.

    settings に OPENSOCIAL_DEBUG=True が記載されていると,
    ローカルデバックであると判断し, 本来は GREE がコールするべき
    Callback Path に, 直接リダイレクトする.
    """
    item_id_base = None
    item_name = None
    item_description = None
    item_quantity = 1
    redirect_path = None
    media_path = None
    callback_path = None

    def payment(self, request, *args, **kwargs):
        """
        GREE にリダイレクトする.
        
        GachaView クラスでは,
        check -> payment -> gacha の順にメソッドを実行するが,
        HttpResponse を返すため, 続く gacha は実行されない.

        callback_path で設定した URL が GREE から呼ばれるので
        そこで gacha メソッドを実行し,
        redirect_path で設定した URL へユーザは遷移するので
        そこで gacha メソッドの終了を待つ.
        """
        self.raise_if_none('item_id_base', 'item_name', 'item_description',
                           'redirect_path', 'media_path', 'callback_path')
        need_coin = self.get_amount(request, *args, **kwargs)
        self.write_log_debug(u'payment: need_coin = %s', need_coin)

        if settings.OPENSOCIAL_DEBUG:
            self.write_log_debug(u'payment: OPENSOCIAL_DEBUG is True')
            # こっそり, callback_path の View に redirect_path を伝える
            self.session.set('gree_coin_redirect_path', self.redirect_path)
            self.write_log_debug(u'payment: redirect to %s', self.callback_path)
            return HttpResponseOpensocialRedirect(self.callback_path)

        # submodule への依存は諦める
        self.write_log_debug(u'payment: opensocial_viewer_id = %s',
                             request.opensocial_viewer_id)
        osuser = get_osuser(request.opensocial_viewer_id, request)
        self.write_log_debug(u'payment: osuser = %s', osuser.userid)

        purchase_url = Payment(request).request_payment(
            osuser_id=osuser.userid,
            item_id=int(self.get_gacha_id()) + int(self.item_id_base),
            item_name=self.item_name,
            item_point=need_coin,
            item_description=self.item_description,
            item_image_url=self.media_path,
            callback_path=self.callback_path,
            finish_path=self.redirect_path,
            item_message='',
            item_quantity=self.item_quantity,
            is_test=False,
        )

        self.write_log_debug(u'payment: redirect to %s', purchase_url)
        return HttpResponseRedirect(purchase_url)

    def get_gacha_kwargs(self, request, *args, **kwargs):
        return {}

    def transaction_context(self, player, **kwargs):
        return NullContext()
