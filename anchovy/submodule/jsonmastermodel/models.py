# -*- coding: utf-8 -*-
"""
マスターデータ向けのモデル。
Json化されたフィクスチャデータを、Djangoのモデルっぽく扱う。

JsonMasterModel を継承したモデルを作れば、
.objecs.get(), .objects.all() .objects.filter() が使える。

ただし、クエリセットのように連結することはできない

"""
from __future__ import unicode_literals
import os
import logging
import inspect
from .manager import JsonMasterModelMeta
from .fields import JsonMasterField
from .exceptions import DoesNotExist as _DoesNotExist,\
    MultipleObjectsReturned as _MultipleObjectsReturned,\
    JsonMasterModelError as _JsonMasterModelError

logger = logging.getLogger('JSONMASTERMODEL')


class JsonMasterModel(object):
    """
    エクセルをJson化したフィクスチャーデータを、そのままDjangoのモデルっぽく扱うクラス。
    継承して、MASTER_DATA_JSON_PATH を定義してください。

    例::

        class HamModel(JsonMasterModel):

            MASTER_DATA_JSON_PATH = '%s/tests/jsonmastermodel-testfixture.json' %\
                                os.path.split(os.path.dirname(__file__))[0]

        HamModel.objects.get_by_id(20)
        HamModel.objects.get(sequence_id=2)
        HamModel.objects.all()
        HamModel.objects.filter(category=2)
    """
    __metaclass__ = JsonMasterModelMeta

    MASTER_DATA_JSON_PATH = None  # 上書きすること。

    DoesNotExist = _DoesNotExist

    MultipleObjectsReturned = _MultipleObjectsReturned

    JsonMasterModelError = _JsonMasterModelError

    @classmethod
    def _fields(cls):
        """
        クラスに定義されている JsonMasterField を、再帰的に探す

        dir() + getattr() でも同じ処理ができるが、そうすると
        @property を暴発させてしまうので vars() + __bases__ で。

        :return: このクラスの持つ JsonMasterField の一覧
            キーがフィールド名(変数名), 値が JsonMasterField のインスタンス
        :rtype: dict
        """
        _fields_dict = dict()
        for base_class in cls.__bases__:
            if hasattr(base_class, '_fields'):
                _fields_dict.update(base_class._fields())

        for name, value in vars(cls).iteritems():
            if isinstance(value, JsonMasterField):
                _fields_dict[name] = value
        return _fields_dict

    @classmethod
    def _cached_fields(cls):
        """
        _fields の取得をクラス変数にキャッシュする

        比較的重い処理なので。
        """
        if not hasattr(cls, '_fields_cache'):
            cls._fields_cache = cls._fields()
        return cls._fields_cache

    def __init__(self, fixture_record_fields, pk=None):
        """
        Json の パース済み dict
        :param fixture_record_fields: fixture json の、fields
        :param pk: fixture json の、pk
        """
        self._pk = self._id = pk
        for field_name, field in self._cached_fields().iteritems():
            value = field._get_value_from_fixture_record_fields(
                fixture_record_fields, field_name)
            setattr(self, field_name, value)

    def __unicode__(self):
        return u'%s:%s' % (self.__class__.__name__, self.id,)

    def __str__(self):
        return self.__unicode__()

    @property
    def id(self):
        """
        :rtype: int
        """
        return self._id

    @property
    def pk(self):
        """
        :rtype: int
        """
        return self._pk

    @classmethod
    def get(cls, pk):
        """
        CachedMasterModel の get と同様、PK(ID)指定でオブジェクトを1つ返す
        :rtype: JsonMasterModel
        """
        return cls.objects.get_by_id(pk)

    @classmethod
    def get_all(cls):
        """
        CachedMasterModel の get_all と同様、全レコードを返す
        :rtype: list
        """
        return cls.objects.all()

    @classmethod
    def get_field_dict(cls, field_name):
        """
        field_nameをキーにしたdictを作って返す。
        プロセスにキャッシュする。

        例:
            cls.get_field_dict('level')
            であれば、level フィールドの値をキーにした dict が返される。
            SQLの検索インデックスの代わりに使うことを想定している。
            ただし、フィールドはユニークなものでないと
            古いレコードが上書きされてしまうので注意すること
        """
        cache_name = '_field_dict_{}'.format(field_name)
        if not hasattr(cls, cache_name):
            d = {getattr(i, field_name): i for i in cls.objects.all()}
            setattr(cls, cache_name, d)
        return getattr(cls, cache_name)

    @classmethod
    def get_field_list_dict(cls, field_name):
        """
        field_name でリスト化し、それをキーにしたdictを作って返す。
        プロセスにキャッシュする。

        cached_property や imagemixin と一緒に使う時は、
        インスタンスがキレイになるよう注意すること。

        例:
            cls.get_field_list_dict('category_id')
            であれば、レコード全てを category_id で分けてリスト化し、
            それをフィールドの値をキーにした dict が返される。
            (つまり、戻り値の dict の value が list になっている)
            SQLの検索インデックスの代わりに使うことを想定している。
        """
        cache_name = '_field_list_dict_{}'.format(field_name)
        if not hasattr(cls, cache_name):
            d = dict()
            for i in cls.objects.all():
                field_value = getattr(i, field_name)
                if not field_value in d:
                    d[field_value] = list()
                d[field_value].append(i)
            setattr(cls, cache_name, d)
        return getattr(cls, cache_name)

    @classmethod
    def quick_filter(cls, **kwargs):
        """
        フィールド名で検索し、一致するレコードを全て返す

        結果として、cls.objects.filter() と似ているが、
        フィクスチャのレコード数が多い場合はこちらの方が早い。
        検索インデックスの代わりに使ってください

        従来は、このメソッドで結果インスタンスをキャッシュし、
        常にプロセス内で同一のインスタンスを返していたが、
        それだと cached_property などを使っているとインスタンスが汚れていく。
        例えば、gtoolkit.image2.mixins.ImageMixin を使う時に、
        FP なのに SP 用の画像が出るなどの問題が発生する可能性があった。

        そのため、メソッドが呼ばれるたびにキレイなインスタンスを作りなおすようにした。
        そして、objects の中にあるのが妥当だと思ったので移動。

        違うインスタンスが返ってくるテストは、
        tests.test_jsonmastermodel_large.
        LargeJsonMasterModelTest.test_quick_filter_different_object
        にある。
        """
        return cls.objects.quick_filter(**kwargs)

    @classmethod
    def load_test_fixture(cls, test_fixture_path):
        """
        テストフィクスチャを読み込む

        もし、test_fixture_path が相対パスであれば、
        **このメソッドを呼び出したファイル**から見ての相対位置でファイルを探す
        """

        if not os.path.isabs(test_fixture_path):
            # パスが相対指定
            # 呼び出し元ファイル。リファクタリングする時注意!
            caller_file_path = inspect.stack()[1][1]
            test_fixture_path = os.path.join(
                os.path.dirname(caller_file_path),
                test_fixture_path
            )

        cls.MASTER_DATA_JSON_PATH = test_fixture_path
        cls.objects.reload()
