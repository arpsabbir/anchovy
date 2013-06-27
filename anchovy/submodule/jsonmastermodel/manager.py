# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
from django.conf import settings
from django.utils.functional import cached_property

from .operators import operators

class MasterDataJsonPathDoesNotDefined(Exception):
    pass


class JsonMasterModelManager(object):

    def __init__(self, model_cls):
        self.model_cls = model_cls

    def _get_master_json_path(self):
        """
        :return: Json ファイル のパス
        """
        master_json_path = getattr(self.model_cls,
                                   'MASTER_DATA_JSON_PATH', None)

        if not master_json_path:
            # JsonMasterModel本体のコンパイル時とかはここでガード
            raise MasterDataJsonPathDoesNotDefined(self.model_cls.__name__)

        if isinstance(master_json_path, (list, tuple)):
            master_json_path = os.path.join(*master_json_path)
        if not os.path.isabs(master_json_path):
            # 絶対パスでない場合は
            if hasattr(settings, 'MASTER_JSON_DIR'):
                # settings.MASTER_JSON_DIR 連結する
                master_json_path = os.path.join(
                    settings.MASTER_JSON_DIR, master_json_path)
            else:
                # MASTER_DATA_JSON_PATHが相対で、かつsettingsに
                # MASTER_JSON_DIR が定義されていない
                raise self.model_cls.JsonMasterModelError(
                    '{} MASTER_DATA_JSON_PATH is not absolute path, '
                    'But settings.MASTER_JSON_DIR is not defined.'
                    .format(self.model_cls.__name__))
        return master_json_path

    def _read_master_data(self):
        """
        :return: パース済み Json データ
            pk, model, fields をキーに持つ dict の list になる
        :rtype: list

        ループでまわしている r はこのようなデータ
        {
          u'pk': 1, u'model':
          u'spam.Test',
          u'fields': {
            u'detail_text': u'\u884c\u52d5\u529b\u3092100%\u56de\u5fa9\u3002',
            u'name': u'\uff77\uff6d\uff71\uff9b\uff6f\uff84\uff9e',
            u'value': 200
          }
        }
        id, pk というキーは通常存在しないが、_filter()にて
        検索で使う可能性があるためつけておく。

        ロックが必要かと思ったが、test_massaccess.py の処理に問題ないので
        必要なさそう。
        """
        master_json_path = self._get_master_json_path()
        records = []
        with open(master_json_path) as fp:
            for r in json.load(fp):
                if not 'id' in r['fields']:
                    r['fields']['id'] = r['pk']
                if not 'pk' in r['fields']:
                    r['fields']['pk'] = r['pk']
                records.append(r)
        return records

    @cached_property
    def _parsed_master_data(self):
        """
        :return: パース済み Json データ
            pk, model, fields をキーに持つ dict の list になる
        :rtype: list
        _parsed_master_data() の結果をキャッシュして持つ。
        """
        return self._read_master_data()

    def reload(self):
        """
        テスト用 リロード
        MASTER_DATA_JSON_PATH をテストフィクスチャに切り替えた後に
        実行する
        """
        self._parsed_master_data = self._read_master_data()
        self._id_dict = {r['pk']: r for r in self._parsed_master_data}  # すまぬ

    def construct_model_instance(self, parsed_master_data_record):
        """
        モデルインスタンスを作成

        :param parsed_master_data_record: パース済みJsonデータの1レコード
        """
        return self.model_cls(parsed_master_data_record['fields'],
                              pk=parsed_master_data_record['pk'])

    @cached_property
    def _id_dict(self):
        """
        :return: レコードのPKを key、レコード自体を value としたdict
        :rtype: dict
        """
        return {r['pk']: r for r in self._parsed_master_data}

    def _filter(self, **kwargs):
        """
        :return: レコードのPKを key、レコード自体を value としたdict
        :rtype: dict
        """
        def _inner_filter(record):
            def _is_cmp(field, k, v):
                for o_k, o_f in operators.items():
                    if k.endswith(o_k):
                        k = k.replace(o_k, "")
                        return o_f(field[k], v)

                return field[k] == v

            return all(
                _is_cmp(record['fields'], k, v) for k, v in kwargs.iteritems()
            )
        return filter(_inner_filter, self._parsed_master_data)

    def all(self):
        """
        :return: 全インスタンスレコード
        :rtype: list

        #_all のシャローコピーを返すので、並べ替えとか間引きをしても良いけど、
        #中身のインスタンスを直接変更してはいけない
        """
        #return copy.copy(self._all)
        return [self.construct_model_instance(r)
                for r in self._parsed_master_data]

    def get_by_id(self, id):
        """
        id指定で1レコード取得する。主要機能

        無ければ DoesNotExist をraise
        ディクショナリを検索するので、.get(id=xx)を使うよりこちらが早い

        例::

            instance = SpamModel.objects.get_by_id(1)
        """
        if not id in self._id_dict:
            raise self.model_cls.DoesNotExist('id:{}'.format(repr(id)))
        r = self._id_dict[id]
        return self.construct_model_instance(r)

    def get(self, **kwargs):
        """
        条件に一致するものを検索 (おまけ機能)

        全レコードを走査するのであまり効率的ではありません
        ID指定で取得する場合は get_by_id を使ってください

        例::

            instance = SpamModel.objects.get(ham_type=2)
        """
        filtered = self._filter(**kwargs)
        if not filtered:
            raise self.model_cls.DoesNotExist(repr(kwargs))
        elif len(filtered) == 1:
            return self.construct_model_instance(filtered[0])
        else:
            raise self.model_cls.MultipleObjectsReturned(repr(kwargs))

    def filter(self, **kwargs):
        """
        param == value を満たすものすべてを抽出し、リストで返す (おまけ機能)

        Djangoのクエリセットのように連結はできません

        例::

            L = SpamModel.objects.filter(ham_type=2)
        """
        return [self.construct_model_instance(r)
                for r in self._filter(**kwargs)]

    def get_field_listed_master_data_dict(self, field_name):
        """
        field_name でリスト化し、それをキーにしたマスターデータのdictを作って返す。
        プロセスにキャッシュする。

        例:
            cls.get_field_listed_master_data_dict('category_id')
            であれば、レコード全てを category_id で分けてリスト化し、
            それをフィールドの値をキーにしたマスターデータの dict が返される。
            (つまり、戻り値の dict の value が list になっている)
            SQLの検索インデックスの代わりに使うことを想定している。

        JsonMasterModel.get_field_list_dict() と似ているが、
        こちらはマスターデータを処理するものであり、JsonMasterModel の
        インスタンスの操作をするわけではない。
        (JsonMasterModelのインスタンスをプロセスにキャッシュしない)
        """
        cache_name = '_field_listed_master_data_dict_{}'.format(field_name)

        if not hasattr(self, cache_name):
            d = dict()
            for r in self._parsed_master_data:
                field_value = r['fields'][field_name]
                if not field_value in d:
                    d[field_value] = list()
                d[field_value].append(r)
            setattr(self, cache_name, d)
        return getattr(self, cache_name)

    def quick_filter(self, **kwargs):
        """
        フィールド名で検索し、一致するレコードを全て返す
        無ければ KeyError。(要望があればこの動作は変えたい)

        完全一致のインデックス検索のように思ってください。

        例::

            cls.objects.quick_filter(boss_id=102)

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

        このメソッドのテストは、tests/test_jsonmastermodel_large.py にある。
        一例だが、
        .objects.filter を使うと 169 ms かかる検索が、
        .quick_filter だと 0 ms で実施できた。
        """
        if len(kwargs) != 1:
            # 1種類の引数(キーバリューペア)のみ受け取る
            raise TypeError(
                'quick_filter takes exactly 1 argument ({} given)'.format(
                    len(kwargs)
                )
            )
        field_name, value = kwargs.items()[0]

        field_listed_master_data_dict = \
            self.get_field_listed_master_data_dict(field_name)
        # 存在しないと KeyError
        # 掴んで別のを投げたり、[] を返したりの選択肢があるが、
        # ひとまずは KeyError をそのまま投げる
        master_data_list = field_listed_master_data_dict[value]

        return [self.construct_model_instance(r)
                for r in master_data_list]


class JsonMasterModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        c = super(JsonMasterModelMeta, mcs).__new__(mcs, name, bases, attrs)
        c.objects = JsonMasterModelManager(c)
        return c
