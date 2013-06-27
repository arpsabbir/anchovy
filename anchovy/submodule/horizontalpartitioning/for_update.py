# -*- coding: utf-8 -*-
from django.db import transaction

import adhoc

class UnmanagedTransactionError(Exception):
    pass


class HasNotLockedError(Exception):
    pass


class ForUpdateObjectsMixin(object):
    """
    FOR UPDATE の scope chain
    """
    def _raise_if_unmanaged(self):
        if adhoc.ON_TEST:
            return

        if not transaction.is_managed(self.db):
            raise UnmanagedTransactionError, self.db

    def select_for_update(self, *args, **kwargs):
        """
        select_for_update を上書きし,
        トランザクション外で使用すると raise する機能を追加.

        QuerySet であるため, _has_locked フラグを設定できない.
        ロックするオブジェクトは一件が望ましいため,
        なるべく get_for_update を使う事.
        """
        self._raise_if_unmanaged()
        return super(ForUpdateObjectsMixin, self).select_for_update(*args, **kwargs)

    def get_for_update(self, **kwargs):
        """
        select_for_update().get() のショートカット
        引数は, get() に渡され, select_for_update() には渡されない.

        _has_locked フラグをオブジェクトに付加する.
        _has_locked は, require_for_update() で使用する.
        """
        obj = self.select_for_update().get(**kwargs)
        obj._has_locked = True
        return obj

    def get_or_create_for_update(self, *args, **kwargs):
        """
        FOR UPDATE 付き get_or_create を行う.
        1 つもなければ作成し、pk で SELECT FOR UPDATE でロックして返す.
        """
        self._raise_if_unmanaged()
        obj, is_created = self.get_or_create(**kwargs)
        obj = self.get_for_update(pk=obj.pk)
        return obj, is_created


class ForUpdateMixin(object):
    """
    FOR UPDATE の partition 隠蔽
    """
    @classmethod
    def get_for_update(cls, player_id, **kwargs):
        """
        get_for_update の partition 隠蔽

        :param string player_id: プレイヤーID
        :param **kwargs: scope chain get_for_update のオプション参照の事
        :return: object
        """
        return cls.objects.partition(player_id).get_for_update(
            player_id=player_id, **kwargs)

    @classmethod
    def get_or_create_for_update(cls, player_id, **kwargs):
        """
        get_or_create_for_update の partition 隠蔽

        :param string player_id: プレイヤーID
        :param **kwargs: scope chain get_or_create_for_update のオプション参照の事
        :return: object
        """
        return cls.objects.partition(player_id).get_or_create_for_update(
            player_id=player_id, **kwargs)


def require_for_update(obj):
    """
    get_for_update によりロックされているオブジェクトでなければ raise する.
    """
    if adhoc.ON_TEST:
        return

    if not getattr(obj, '_has_locked', False):
        raise HasNotLockedError, obj

class RequireForUpdateMixin(object):
    def require_for_update(self):
        require_for_update(self)
