# -*- coding: utf-8 -*-
from django.db import models
from gtoolkit import generate_uuid, datetime
from gtoolkit.db.fields import UniqueIDField

def include(include_path):
    """
    :param
        include_path (extension.module.item.models.effect.ItemEffect)
    :return:
        module
    """
    if include_path is None:
        return None

    module_path = '.'.join(include_path.split('.')[:-1])

    try:
        module = __import__(module_path)
    except ImportError:
        return None
    else:
        for path in include_path.split('.')[1:]:
            try:
                module = getattr(module, path)
            except AttributeError:
                return None

        return module


class FakeMasterModelMeta(type):
    """
    extensionにfixturesが定義してあればそれを優先に使う
    """
    def __new__(mcls, name, bases, attrs):
        cls = type.__new__(mcls, name, bases, attrs)
        if name == 'FakeMasterModel':
            return cls

        cls_module = cls.__module__
        if '.'.join(cls_module.split('.')[:1]) == "extension":
            cls_module = '.'.join(cls_module.split('.')[1:])

        excls = include('extension.%s.%s' % (cls_module, cls.__name__))

        if excls:
            cls.fixtures = excls.fixtures

        return cls

class FakeMasterModel(object):
    """
    マスターデータだが DB に保存するほどでもないモデル.

    fixtures プロパティに含まれるディクショナリから,
    オブジェクトのプロパティを生成する.
    """
    __metaclass__ = FakeMasterModelMeta

    fixtures = {}

    class DoesNotExist(Exception):
        pass

    def __init__(self, pk):
        fixture = self.fixtures.get(pk)

        if fixture is None:
            raise self.DoesNotExist(pk)

        for attr in ['pk', 'id']:
            setattr(self, attr, pk)

        for attr in fixture:
            setattr(self, attr, fixture[attr])

    @classmethod
    def get(cls, pk):
        return cls(pk)

    @classmethod
    def get_all(cls):
        return [cls(pk) for pk in cls.fixtures.iterkeys()]


class UniqueIDFieldMixin(models.Model):
    """
    Model に unique_id を追加する.
    unique_id の値は自動で入るため, 意図的に設定する必要はない.
    unique_id の値は, 物理サーバを跨いで一意である事が保証されている.

    unique=True 制約をつけたい所ではあるが,
    ロジカルデリートと組み合わせると完全に一意にはできない.
    その場合は, unique_id フィールドと 削除時の deleted_uuid とで
    unique_together 制約をつけれると, データの整合性を保てる.
    """

    class Meta:
        abstract = True

    unique_id = UniqueIDField(db_index=True)


class NameFieldMixin(models.Model):
    """
    Model に name と description を追加する.
    """

    class Meta:
        abstract = True

    name = models.CharField(max_length=32)
    description = models.TextField(blank=True)


class DateTimeFieldMixin(models.Model):
    """
    Model に created_at と updated_at を追加する.
    日付は自動で入るため, 意図的に追加/更新する必要はない.
    """

    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EnableFlagScopeMixin(object):
    def enables(self):
        return self.filter(is_enable=True)


class EnableFlagManager(models.Manager):
    """
    EnableFlagMixin から使用するカスタム Manager.

    objects の上書きが必要となる Mix-in クラスを
    EnableFlagMixin と共に利用する場合,
    objects に, その Mix-in クラスのカスタム Manager と
    EnableFlagManager を多重継承した, 新たなカスタム Manager を入れる.

    前述を考慮しなければ, このクラスは,
    EnableFlagMixin のインナークラスでも良い.
    """

    def get_query_set(self):
        return super(EnableFlagManager,
                     self).get_query_set().filter(is_enable=True)


class EnableFlagMixin(models.Model):
    """
    Model に無効フラグを追加.
    delete() メソッドで is_enable フラグに False が入る.
    objects にカスタム Manager を入れているため,
    filter や get で is_enable=False のフィールドを取り出す事はできない.
    """

    class Meta:
        abstract = True

    objects = EnableFlagManager()

    is_enable = models.BooleanField(db_index=True, default=True)

    def delete(self, using=None):
        self.is_enable = False
        self.save()


class _CheckTermMixin(object):
    """
    期間内かチェック関数を持つクラス
    """

    def _is_on_term(self, now, start_at, end_at):
        """
        期間内なら True

        基本は, start_at <= now <= end_at であれば良く,
        比較可能であれば start_at, now, end_at の型は問わない.
        """
        if start_at is None and end_at is None:
            # 開始時間も終了時間も未入力の時は、期間内
            return True

        if start_at is None:
            # 開始時間が未入力
            return now < end_at

        if end_at is None:
            # 終了時間が未入力
            return now > start_at

        # 期間内か判定
        return start_at <= now <= end_at


class TermObjectsMixin(object):
    """
    django.db.models.Manager と
    django.db.models.query.QuerySet に
    Mix-in して使うクラス.
    """

    def is_in_term(self):
        now = datetime.now()
        return self.filter(start_at__lte=now, end_at__gt=now)


class TermMixin(_CheckTermMixin, models.Model):
    """
    有効期限を管理するため, Model に start_at と end_at を追加する.
    """

    class Meta:
        abstract = True

    start_at = models.DateTimeField(null=True, blank=True, default=None)
    end_at = models.DateTimeField(null=True, blank=True, default=None)

    @property
    def is_in_term(self):
        """
        期間外なら False
        """
        now = datetime.now()
        return self._is_on_term(now, self.start_at, self.end_at)


class CycleBasedModel(_CheckTermMixin, models.Model):
    """
    Cycle class のベースクラス
    """

    class Meta:
        abstract = True

    def is_active(self):
        return True


class MonthlyCycleMixin(CycleBasedModel):
    """
    月毎に実行するタスクを管理
    """

    class Meta:
        abstract = True

    month_start_at = models.IntegerField(default=0)
    month_end_at = models.IntegerField(default=0)

    def is_active(self):
        """
        毎月、指定された日付の間であれば有効

        :return:
        :rtype: bool
        """
        # 多重継承で他クラスで期間外判定なら期間外とする
        result = super(MonthlyCycleMixin, self).is_active()
        if not result:
            return False

        # 現在の日付 dd
        now = datetime.now().day
        if self.month_end_at == 0:
            # 終了日未設定の場合は月末まで
            return self._is_on_term(now, self.month_start_at, None)
        else:
            return self._is_on_term(now, self.month_start_at, self.month_end_at)


class WeeklyCycleMixin(CycleBasedModel):
    """
    毎週、指定曜日に有効になるロジック

    日、月、火、水、木、金、土
    """

    class Meta:
        abstract = True

    sunday_enable = models.BooleanField(default=False)
    monday_enable = models.BooleanField(default=False)
    tuesday_enable = models.BooleanField(default=False)
    wednesday_enable = models.BooleanField(default=False)
    thursday_enable = models.BooleanField(default=False)
    friday_enable = models.BooleanField(default=False)
    saturday_enable = models.BooleanField(default=False)

    WEEK_COLUMN_DICT = {
        0: 'monday_enable',
        1: 'tuesday_enable',
        2: 'wednesday_enable',
        3: 'thursday_enable',
        4: 'friday_enable',
        5: 'saturday_enable',
        6: 'sunday_enable'
    }

    def is_active(self):
        """
        今日が設定された曜日なら有効

        :return:
        :rtype: bool
        """
        # 多重継承で他クラスで期間外判定なら期間外とする
        result = super(WeeklyCycleMixin, self).is_active()
        if not result:
            return False

        return self.check_day_of_the_week()

    def check_day_of_the_week(self):
        """
        今日の曜日をチェックする

        :return: 今日が対象の曜日に含まれるか
        :rtype: bool
        """
        return getattr(self, self.get_day_of_the_week_column())

    def get_day_of_the_week_column(self):
        """
        現在の曜日のカラム名を返す

        :return:
        :rtype: str
        """
        return self.WEEK_COLUMN_DICT.get(datetime.now().weekday())


class DailyCycleMixin(CycleBasedModel):
    """
    毎日、指定時間に有効になるロジック
    """

    class Meta:
        abstract = True

    day_start_at = models.IntegerField(default=0)
    day_end_at = models.IntegerField(default=0)

    def is_active(self):
        """
        現在、指定時間内であれば有効

        :rtype: bool
        """
        # 多重継承で他クラスで期間外判定なら期間外とする
        result = super(DailyCycleMixin, self).is_active()
        if not result:
            return False

        # 現在の時間 hhmm (type int)
        now = datetime.now().hour * 100 + datetime.now().minute

        if self.day_end_at == 0:
            # 終了時間未設定の場合は終日
            return self._is_on_term(now, self.day_start_at, None)
        else:
            return self._is_on_term(now, self.day_start_at, self.day_end_at)


class PriorityMixin(models.Model):
    """
    並び替え用のpriorityフィールドを追加するMixin
    """

    class Meta:
        abstract = True

    priority = models.IntegerField(default=100, db_index=True)


class SortablePriorityMixin(object):
    """
    マスターモデルに priority フィールドを持つ場合,
    毎回ソート用の比較関数を書くのを避けるために定義された Mix-in クラス.

    has_priority_field で priority プロパティを返すモデルを返す事.
    priority は, 値が大きいほど優先度が高い.

    使用方法は次の通り.

    .. code-block:: python

        class Egg(CachedMasterModel):
            priority = models.IntegerField()


        class PlayerEggModel(SortablePriorityMixin, PlayerHasManyModel):
            egg_id = models.IntegerField()

            @property
            def egg(self):
                return Egg.get(self.egg_id)

            def has_priority_filed(self):
                return self.egg

            def get_sorted_list(self):
                objs = self.gets_by(self.player_id)
                return sorted(objs, self.priority_cmp)
    """

    def has_priority_field(self):
        raise NotImplementedError

    @classmethod
    def priority_cmp(cls, a, b):
        a_field = a.has_priority_field()
        b_field = b.has_priority_field()

        if a_field.priority < b_field.priority:
            return 1
        elif a_field.priority > b_field.priority:
            return -1
        elif a.id < b.id:
            return 1
        elif a.id > b.id:
            return -1
        else:
            return 0
