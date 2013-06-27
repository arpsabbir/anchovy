# -*- coding: utf-8 -*-
"""
HorizontalPartitioningModel や LogicalDeleteModel を継承したモデルに
OrCreateMixin を Mix-in すると get_or_create と update_or_create が使える.

PlayerHasManyModel と PlayerHasOneModel は Mix-in 済み.
"""
from django.db import transaction, IntegrityError

class OrCreateMixin(object):
    @classmethod
    def get_or_create(cls, player_id, **kwargs):
        """
        get_or_create の partition 隠蔽

        :param string player_id: プレイヤーID
        :param **kwargs: get_or_create のオプション参照の事
        :return: object, created
        """
        return cls.objects.partition(player_id).get_or_create(
            player_id=player_id, **kwargs)

    @classmethod
    def update_or_create(cls, player_id, **kwargs):
        """
        更新または追加を行う.

        :param string player_id: プレイヤーID
        :param **kwargs: get_or_create と同様
        :return: object, created, updated
        """
        obj, created = cls.get_or_create(player_id, **kwargs)
        if created:
            return obj, True, False

        defaults = kwargs.pop('defaults', {})
        params = dict([(k, v) for k, v in kwargs.items() if '__' not in k])
        params.update(defaults)
        for attr, val in params.items():
            if hasattr(obj, attr):
                setattr(obj, attr, val)

        try:
            sid = transaction.savepoint()
            obj.save(force_update=True)
            transaction.savepoint_commit(sid)
            return obj, False, True
        except IntegrityError, e:
            transaction.savepoint_rollback(sid)
            try:
                return cls.objects.partition(player_id).get(**kwargs), False, False
            except cls.DoesNotExist:
                raise IntegrityError, e
        except:
            transaction.savepoint_rollback(sid)
            raise
