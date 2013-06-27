# -*- coding: utf-8 -*-
"""
水平分割に論理削除を追加する.
"""
from django.db import models
from django.db.models.query import QuerySet

# TODO: gtoolkit 依存をやめる
# 将来的に horizontalpartitioning から論理削除を外す
from gtoolkit import generate_uuid, datetime

class LogicalDeleteObjectsMixin(object):
    def by_alive(self):
        """
        有効なレコードのみ返す
        """
        return self.filter(deleted_uuid='')

    def delete(self):
        return self.update(deleted_uuid=generate_uuid(),
                           deleted_at=datetime.now())

    def physical_delete(self):
        return super(LogicalDeleteObjectsMixin, self).delete()


class LogicalDeleteQuerySet(LogicalDeleteObjectsMixin, QuerySet):
    pass


class LogicalDeleteManager(LogicalDeleteObjectsMixin, models.Manager):
    """
    DB水平分割マネージャに論理削除の機能を追加したマネージャ
    """
    def get_query_set(self):
        """
        新しい Manager を作成し,
        get_query_set() を上書きするのであれば,
        必ず内部で by_alive() を使用する事.
        """
        return LogicalDeleteQuerySet(self.model).by_alive()


class LogicalDeleteModel(models.Model):
    """
    論理削除用のフィールドやメソッドを追加する
    """
    class Meta:
        abstract = True


    class RedeletedError(Exception):
        pass


    objects = LogicalDeleteManager()

    # delete_at を有効/無効の確認に利用すると,
    # 一意キー制約を設けた際に, 一秒以内の delete が使えないため,
    # 有効/無効を判断するための UUID フィールドを設ける.
    # 初期値に NULL を指定すると, NULL はレコード毎に異なる値と認識されるため,
    # UUID フィールドを一意キー制約に含められない.
    # そこで, 初期値には空文字列を明示的に指定しておく.
    deleted_uuid = models.CharField(max_length=255, db_index=True, default='')

    # 念のため, 記録として削除日時を残しておく.
    deleted_at = models.DateTimeField(blank=True, null=True)

    def delete(self):
        if self.deleted_uuid:
            raise self.RedeletedError, self.pk

        self.deleted_uuid = generate_uuid()
        self.deleted_at = datetime.now()
        self.save()

    def physical_delete(self):
        return super(LogicalDeleteModel, self).delete()
