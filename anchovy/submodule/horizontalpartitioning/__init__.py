# -*- coding: utf-8 -*-
import hashlib
import random

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet

from for_update import ForUpdateObjectsMixin

class HorizontalPartitioningQuerySet(ForUpdateObjectsMixin,
                                     QuerySet):
    pass


class HorizontalPartitioningManager(ForUpdateObjectsMixin,
                                    models.Manager):
    """
    Manager for DB horizontal partitioning.
    Add "objects = HorizontalPartitioningManager()" at model.
    DB水平分割マネージャ
    モデルに、objects = HorizontalPartitioningManager() を書くこと
    """

    def partition(self, user_id):
        """
        Return the manager that "using" DB which contain information of user_id.
        user_idのユーザー情報が入っているDBをusingしたマネージャを返す
        """
        database_name = get_horizontal_partitioning_database_name(user_id)
        return self.using(database_name)

    def random_partition(self):
        """
        ランダムに選択したシャードを使用した Manager を返す.
        """
        salt = unicode(random.randint(1, 999))
        database_name = get_horizontal_partitioning_database_name(salt)
        return self.using(database_name)

    def use_shard(self, shard_id):
        """
        shard_idのDBをusingしたManagerを返す
        """
        db_name = settings.HORIZONTAL_PARTITIONING_DB_NAME_FORMAT % shard_id
        return self.using(db_name)

    def multi_partition_filter(self, user_id_list, **kwargs):
        """
        Searches DBs and return the results at one time.
        複数のDBを順番に検索し、結果を結合して返す
        @return (list)検索結果 クエリセットではない
        ※ in句を使った場合、そのパーティションにあきらかに存在しないデータに対しても検索を行なってしまう。
        →改善の必要あり。in句でユーザーIDを指定する場合は、別のメソッドを用意すると良いかも。
        """
        d = {}  # DB名をキー、ユーザー一覧をvalueとしたリスト
        for user_id in user_id_list:
            database_name = get_horizontal_partitioning_database_name(user_id)
            if not database_name in d:
                d[database_name] = []
            d[database_name].append(user_id)
        res = []
        for database_name, user_id_list in d.iteritems():
            qs = self.using(database_name).filter(**kwargs)
            res += list(qs)
        return res

    def all_partitions(self):
        """
        Return the managers of every partitions with generator.
        For batch or analytics use.
        全パーティションのマネージャーをジェネレータ(イテレータ)で順番に返す
        通常は使わない。主にバッチや集計用。
        """
        for i in range(settings.HORIZONTAL_PARTITIONING_PARTITION_NUMBER):
            database_name = settings.HORIZONTAL_PARTITIONING_DB_NAME_FORMAT % i
            yield self.using(database_name)

    def all_partition_filter(self, **kwargs):
        """
        Return the results after searching every partitions.
        For batch or analytics use.
        全パーティションを検索し、結果を結合して返す
        通常は使わない。主にバッチや集計用。
        """
        res = []
        for m in self.all_partitions():
            qs = m.filter(**kwargs)
            res += list(qs)
        return res

    def all_partition_count(self, **kwargs):
        """
        Return the sum of count after searching every partitions.
        For batch or analytics use.
        全パーティションを検索し、countの結果を合計して返す
        通常は使わない。主にバッチや集計用。
        """
        n = 0
        for m in self.all_partitions():
            n += m.filter(**kwargs).count()
        return n

    def get_query_set(self):
        return HorizontalPartitioningQuerySet(self.model)


class HorizontalPartitioningMixin(object):
    """
    DB horizontal partitioning mixin.

    DB水平分割 MixIn
    継承先のモデルで、HorizontalPartitioningManager も組み込んでください
    objects = HorizontalPartitioningManager()
    """
    ENABLE_HORIZONTAL_PARTITIONING = True #Don`t change True固定。
    #Judge duck typing using DB router or else.Better using issubclass?
    #▲DBルータなどでダックタイピング判定する。issubclassの方が良い?

    HORIZONTAL_PARTITIONING_KEY_FIELD = 'player_id'
    #Use this field for partition.You override this as class variance to change the value.
    #▲このフィールドをパーティションに使う。変更する場合、クラス変数で上書きする

    @property
    def horizontal_partitioning_database_name(self):
        """
        The name of DB this instance used at horizontal partitioning.
        このクラスのインスタンスが水平分割の際使うDB名
        """
        basekey = getattr(self, self.HORIZONTAL_PARTITIONING_KEY_FIELD)
        if hasattr(basekey, 'pk'):
            #リレーションしているモデル(Playerなど)だった
            basekey = basekey.pk
        return get_horizontal_partitioning_database_name(basekey)


def get_horizontal_partitioning_database_name(user_id):
    """
    Return the name of hash DB from user_id(osuser_id,player_id)
    user_id can be str or unicode.
    user_id (osuser_id, player_id)からハッシュDB名を返す
    user_id は str でも unicode でも同じ値になる

    When you migrate data using MySQL,doing like
    SELECT CONV(RIGHT(SHA1('USER-ID'),1), 16, 10); or
    SELECT MOD(CONV(RIGHT(SHA1('USER-ID'),2), 16, 10), 16);
    will make it.

    MySQLでデータマイグレーションを行う場合は、
    SELECT CONV(RIGHT(SHA1('USER-ID'),1), 16, 10); や
    SELECT MOD(CONV(RIGHT(SHA1('USER-ID'),2), 16, 10), 16); という感じで行う

    >>> from horizontalpartitioning import get_horizontal_partitioning_database_name
    >>> get_horizontal_partitioning_database_name('12346')
    'part2'
    >>> get_horizontal_partitioning_database_name(u'12346')
    'part2'
    >>> get_horizontal_partitioning_database_name(12346)
    TypeError: must be string or buffer, not int
    """
    user_id = str(user_id) if isinstance(user_id, (int, long)) else user_id
    hex_hash = hashlib.sha1(user_id).hexdigest()
    group_number = (int(hex_hash[-2:], 16) % settings.HORIZONTAL_PARTITIONING_PARTITION_NUMBER)
    #▲ハッシュ文字列の下2桁を16進数にしてDB振り分け。256台まではこれで大丈夫。スライスした方がちょっとだけ早かった
    #むしろ下1桁だけ見ればいい気もするが、ローカルで%4などで使うケースもあるのでこれで良い
    return settings.HORIZONTAL_PARTITIONING_DB_NAME_FORMAT % group_number
