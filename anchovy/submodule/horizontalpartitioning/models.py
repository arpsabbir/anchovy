# -*- coding: utf-8 -*-
from django.db import models

from __init__ import (HorizontalPartitioningQuerySet,
                      HorizontalPartitioningManager,
                      HorizontalPartitioningMixin)
from or_create import OrCreateMixin
from for_update import ForUpdateMixin, RequireForUpdateMixin
from logical_delete import LogicalDeleteObjectsMixin, LogicalDeleteModel
from memoize import MemoizedQuerySet, clear_request_memoize_cache_query

class HorizontalPartitioningModel(OrCreateMixin,
                                  ForUpdateMixin,
                                  RequireForUpdateMixin,
                                  HorizontalPartitioningMixin,
                                  models.Model):
    """
    特定のキーを使ってテーブルを水平分割するモデル
    プレイヤー対応のモデルはこれを継承すれば水平分割できる

    You can implement horizontal partitioning by inherit this class (at your models)
    """
    objects = HorizontalPartitioningManager()

    class Meta:
        abstract = True


class PlayerQuerySet(MemoizedQuerySet, # メモ化優先
                     LogicalDeleteObjectsMixin,
                     HorizontalPartitioningQuerySet):
    pass


class PlayerManager(LogicalDeleteObjectsMixin,
                    HorizontalPartitioningManager):
    def get_query_set(self):
        return PlayerQuerySet(self.model).by_alive()


class _MatchedPlayerIDMixin(object):
    class UnmatchedPlayerIDError(Exception):
        pass


    def check_player_id_or_raise(self, player_id):
        """
        self.player_id と player_id が異なるのであれば raise で落とす.
        """
        if self.player_id != player_id:
            raise self.UnmatchedPlayerIDError, (self.player_id, player_id)


class _CreateMixin(object):
    @classmethod
    def create(cls, player_id, *args, **kwargs):
        """
        create の partition 隠蔽

        :param string player_id: プレイヤーID
        :return: 作成したオブジェクト
        """
        return cls.objects.partition(player_id).create(player_id=player_id,
                                                       *args, **kwargs)

    @classmethod
    def bulk_create(cls, player_id, objs, batch_size=None):
        """
        bulk_create の partition 隠蔽

        :param player_id: プレイヤーID
        :type player_id: string

        :param objs: 生成するオブジェクトデータのdictのリスト
        :type objs: list

        :return: 作成したオブジェクト
        """
        return cls.objects.partition(player_id).bulk_create(
            [cls(player_id=player_id, **obj) for obj in objs],
            batch_size=batch_size
        )


class PlayerHasManyModel(_MatchedPlayerIDMixin,
                         _CreateMixin,
                         HorizontalPartitioningModel,
                         LogicalDeleteModel):
    """
    Playerと1:Nの関係をもつモデル
    """
    class Meta:
        abstract = True
        # get_or_create を使う場合, unique_together を必ず定義する事
        # unique_together には, player_id と deleted_uuid を必ず含める事


    objects = PlayerManager()

    player_id = models.CharField(max_length=255, db_index=True)

    @classmethod
    def get(cls, player_id, *args, **kwargs):
        """
        get の partition 隠蔽

        :param string player_id: プレイヤーID
        :param any pk: 一意キー
        :return: objects
        """
        # Todo: このゴミを誰か直してくれ
        if len(args) == 1:
            kwargs['pk'] = args[0]
        return cls.objects.partition(player_id).get(player_id=player_id, **kwargs)

    @classmethod
    def by_player(cls, player_id):
        """
        filter の partition 隠蔽

        :param string player_id: プレイヤーID
        :return: objects
        """
        return cls.objects.partition(player_id).filter(player_id=player_id)

    def save(self, *args, **kwargs):
        """
        メモ化キャッシュを削除するため save をフックする.
        論理削除の delete で save を実行しているので delete はフックしない.
        """
        clear_request_memoize_cache_query()
        return super(PlayerHasManyModel, self).save(*args, **kwargs)


class PlayerHasOneModel(_MatchedPlayerIDMixin,
                        _CreateMixin,
                        HorizontalPartitioningModel,
                        LogicalDeleteModel):
    """
    Playerと1:1の関係をもつモデル
    """
    class Meta:
        abstract = True
        unique_together = ('player_id', 'deleted_uuid')


    objects = PlayerManager()

    player_id = models.CharField(max_length=255, db_index=True)

    @classmethod
    def get(cls, player_id):
        """
        get の partition 隠蔽

        :param string player_id: プレイヤーID
        :return: 取得できたオブジェクト
        """
        return cls.objects.partition(player_id).get(player_id=player_id)


class PlayerPKModel(_MatchedPlayerIDMixin,
                    _CreateMixin,
                    HorizontalPartitioningModel):
    """
    Playerと1:1の関係を持つ、PlayerHasOneModel から
    LogicalDeleteModel を抜いたもの

    player_id がプライマリキーとなる。
    LogicalDelete の deleted_uuid の不要なインデックスが作られない。
    削除運用を考えない、プレイヤーと 1to1 のモデルに使う。
    PlayerManagerは標準搭載してないので注意
    """
    class Meta:
        abstract = True

    player_id = models.CharField(max_length=255, primary_key=True)

    @classmethod
    def get(cls, player_id):
        """
        get の partition 隠蔽

        :param string player_id: プレイヤーID
        :return: 取得できたオブジェクト
        """
        return cls.objects.partition(player_id).get(player_id=player_id)
