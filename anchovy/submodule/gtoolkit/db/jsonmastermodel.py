# -*- coding: utf-8 -*-
"""
マスターデータ向けのモデル。
Json化されたフィクスチャデータを、Djangoのモデルっぽく扱う。

JsonMasterModel を継承したモデルを作れば、
.objecs.get(), .objects.all() .objects.filter() が使える。

ただし、クエリセットのように連結することはできない


Django起動時にJsonからロードされ、データはメモリ上に保持されます。
runserver している場合は再起動すると反映されます。

各インスタンスはプロセス内で唯一のものとなり、
get した時などにインスタンスを新しく作ったりはしません。
そのため、インスタンス変数に値を格納すると、
それはプロセスが終了するまで保持されることになります。
プレイヤーやその時の一時的な状態に左右されるような変数は
格納しないでください。
"""
import os
import copy

from django.utils import simplejson
from django.conf import settings


class JsonMasterModelManager(object):
    def __init__(self, model_cls):
        self.model_cls = model_cls

        master_json_path = getattr(model_cls, 'MASTER_DATA_JSON_PATH', None)

        if not master_json_path:
            # JsonMasterModel本体のコンパイル時とかはここでガード
            return

        if isinstance(master_json_path, (list, tuple)):
            master_json_path = os.path.join(*master_json_path)
        if not os.path.isabs(master_json_path):
            # 絶対パスでない場合は
            if hasattr(settings, 'MASTER_JSON_DIR'):
                # settings.MASTER_JSON_DIR 連結する
                master_json_path = os.path.join(settings.MASTER_JSON_DIR, master_json_path)
            else:
                # MASTER_DATA_JSON_PATHが相対で、かつsettingsに MASTER_JSON_DIR が定義されていない
                raise model_cls.JsonMasterModelError(
                    '{} MASTER_DATA_JSON_PATH is not absolute path, '
                    'But settings.MASTER_JSON_DIR is not defined.'
                    .format(model_cls.__name__))

        self._all = []
        self._id_dict = {}

        with open(master_json_path) as fp:
            for r in simplejson.load(fp):
                instance = self.model_cls(r['fields'], pk=r['pk'])
                self._all.append(instance)
                self._id_dict[r['pk']] = instance

    def all(self):
        u"""
        全レコードを取得して返す
        """
        if not hasattr(self, '_all'):
            raise self.model_cls.JsonMasterModelError(
                '%s MASTER_DATA_JSON_PATH is not overrided.' % self.model_cls.__name__)
        return copy.copy(self._all)

    def get_by_id(self, id):
        u"""
        id指定で1レコード取得する。主要機能

        無ければ DoesNotExist をraise
        ディクショナリを検索するので、.get(id=xx)を使うよりこちらが早い

        例::

            instance = SpamModel.objects.get_by_id(1)
        """
        if not hasattr(self, '_id_dict'):
            raise JsonMasterModelManager(
                '%s MASTER_DATA_JSON_PATH is not overrided.' % self.model_cls.__name__)
        instance = copy.copy(self._id_dict.get(id, None))
        if not instance:
            raise self.model_cls.DoesNotExist('id:{}'.format(repr(id)))
        return instance

    def get(self, **kwargs):
        """
        条件に一致するものを検索 (おまけ機能)

        全レコードを走査するのであまり効率的ではありません
        ID指定で取得する場合は get_by_id を使ってください

        例::

            instance = SpamModel.objects.get(ham_type=2)
        """
        filtered = self.filter(**kwargs)
        if not filtered:
            raise self.model_cls.DoesNotExist(repr(kwargs))
        elif len(filtered) == 1:
            return filtered[0]
        else:
            raise self.model_cls.MultipleObjectsReturned(repr(kwargs))

    def filter(self, **kwargs):
        """
        param == value を満たすものすべてを抽出し、リストで返す (おまけ機能)

        Djangoのクエリセットのように連結はできません

        例::

            L = SpamModel.objects.filter(ham_type=2)
        """
        def _filter(record):
            return all(
                getattr(record, k) == v for k, v in kwargs.iteritems()
            )
        return filter(_filter, self._all)


class JsonMasterModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        c = super(JsonMasterModelMeta, mcs).__new__(mcs, name, bases, attrs)
        c.objects = JsonMasterModelManager(c)
        return c


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

    class DoesNotExist(Exception):
        pass

    class MultipleObjectsReturned(Exception):
        pass

    class JsonMasterModelError(Exception):
        pass

    def __init__(self, bare_record, pk=None):
        if pk:  # PKがある場合は明示的につける。普通ある。
            setattr(self, 'id', pk)
            setattr(self, 'pk', pk)
        for k, v in bare_record.iteritems():
            # もしここで Attribute Error が出てしまう場合は、
            # 同名のプロパティやメソッドが無いかチェック
            setattr(self, k, v)  # 同名のプロパティやメソッドは無いか?

    def __unicode__(self):
        return u'%s:%s' % (self.__class__.__name__, self.id,)

    def __str__(self):
        return self.__unicode__()

    @classmethod
    def get(cls, pk):
        u"""
        CachedMasterModel の get と同様、PK(ID)指定でオブジェクトを1つ返す
        """
        return cls.objects.get_by_id(pk)

    @classmethod
    def get_all(cls):
        u"""
        CachedMasterModel の get_all と同様、全レコードを返す
        """
        return cls.objects.all()

    @classmethod
    def get_field_dict(cls, field_name):
        u"""
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
        u"""
        field_name でリスト化し、それをキーにしたdictを作って返す。
        プロセスにキャッシュする。

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
        u"""
        フィールド名で検索し、一致するレコードを全て返す
        無ければ KeyError。(要望があればこの動作は変えたい)

        完全一致のインデックス検索のように思ってください。

        例::

            cls.quick_filter(boss_id=102)

        条件は複数指定はできず、1つだけ指定できる。

        :return: 一致するレコードのリスト
        :rtype: list

        動作解説::

            boss_id=102 で検索した場合…

            全レコードで、
            「キーがboss_idで、valueが該当レコードのリストの入ったディクショナリ」
            を作る。(これはクラス変数にキャッシュされる)

            そのディクショナリの、キー = 102 を検索して、返す

            ディクショナリ分のメモリを使うが、
            ハッシュテーブルの検索なので全レコードを線形に検索するより早い。
        """
        if len(kwargs) != 1:
            # 1種類の引数(キーバリューペア)のみ受け取る
            raise TypeError(
                'quick_filter takes exactly 1 argument ({} given)'.format(
                    len(kwargs)
                )
            )
        field_name, value = kwargs.items()[0]
        field_list_dict = cls.get_field_list_dict(field_name)
        # 存在しないと KeyError
        # 掴んで別のを投げたり、[] を返したりの選択肢があるが、
        # ひとまずは KeyError をそのまま投げる
        return field_list_dict[value]
