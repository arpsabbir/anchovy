# -*- coding: utf-8 -*-
from django.core.exceptions import ImproperlyConfigured

RAISE_MESSAGE = "'{0}' must define '{1}'"


class RaiseExceptionMixin(object):
    """
    実装が無いよ〜! を raise する基本機能を, gacha の下に定義したくない
    """

    def raise_not_impl(self, method_name):
        """
        メソッドの実装が存在しない場合に使用
        """
        raise NotImplementedError(
            RAISE_MESSAGE.format(self.__class__.__name__, method_name))

    def raise_imp_conf(self, conf_name):
        """
        プロパティの値が存在しない場合に使用
        """
        raise ImproperlyConfigured(
            RAISE_MESSAGE.format(self.__class__.__name__, conf_name))

    def raise_if_none(self, *conf_names):
        """
        与えられたアトリビュート名に紐づいた値が None であれば
        raise ImproperlyConfigured() する
        """
        for conf_name in conf_names:
            if getattr(self, conf_name, None) is None:
                self.raise_imp_conf(conf_name)


KEY_PREFIX = 'gacha'


class HasKeyPrefix(RaiseExceptionMixin):
    """
    セッションや KVS で利用するキー名の接頭辞を持つトレイト.
    ガチャ ID とプレイヤー ID で一意にするだけ.
    """

    def set_key_prefix(self, gacha_id, player_id):
        self._key_prefix = ':'.join([KEY_PREFIX,
                                         str(gacha_id),
                                         str(player_id)])

    def build_key(self, key):
        self.raise_if_none('_key_prefix')
        return self._key_prefix + ':' + str(key)


class HasGachaIDMixin(RaiseExceptionMixin):
    """
    必ず __init__ で self.gacha_id を初期化する事.
    このトレイトは実装なので, 新たに継承して実装を作る必要は無い.
    """
    gacha_id = None
 
    def get_gacha_id(self):
        self.raise_if_none('gacha_id')
        return self.gacha_id


class NullContext(object):
    """
    with で使用する何もしないコンテキスト
    """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return True if exc_type is None else False
