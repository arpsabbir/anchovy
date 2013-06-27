# -*- coding: utf-8 -*-

import msgpack
import base64

from django.db import models
from django.utils import simplejson

from gtoolkit import generate_uuid


class ObjectField(models.Field):
    description = u'msgpack でシリアライズ可能なオブジェクトを保存できる'

    __metaclass__ = models.SubfieldBase

    def __init__(self,
                 packb_kwargs={}, unpackb_kwargs={},
                 *args, **kwargs):
        load_object_field()
        self._packb_kwargs = packb_kwargs
        self._unpackb_kwargs = unpackb_kwargs
        super(ObjectField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def to_python(self, value):
        if value is None:
            return value
        if not type(value) in [str, unicode]:
            return value
        return msgpack.unpackb(base64.b64decode(value), **self._unpackb_kwargs)

    def get_db_prep_save(self, value, connection):
        if value is None:
            return
        return base64.b64encode(msgpack.packb(value, **self._packb_kwargs))


class UniqueIDField(models.CharField):
    description = u'インスタンスsave時に、ユニークIDを自動的に格納するフィールド'

    def __init__(self, *args, **kwargs):
        """
        :param generator: ユニークID生成関数、指定が無ければ generate_uuid
        :param max_length: フィールドの文字列数。
                           指定が無ければ generator を1回動かし、その長さとする
        """
        self.generator = kwargs.pop('generator', generate_uuid)
        kwargs.setdefault('max_length', len(self.generator()))
        super(UniqueIDField, self).__init__(*args, **kwargs)


    def pre_save(self, model_instance, add):
        if add and not getattr(model_instance, self.attname):
            value = self.generator()
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super(UniqueIDField, self).pre_save(model_instance, add)


def load_object_field():
    try:
        from south.modelsinspector import add_introspection_rules
    except ImportError:
        pass
    else:
        add_introspection_rules(
            [([ObjectField], [], {}),],
            ["^gtoolkit\.db\.fields\.ObjectField"])
        add_introspection_rules(
            [([UniqueIDField], [], {}),],
            ["^gtoolkit\.db\.fields\.UniqueIDField"])


class JsonDataField(models.Field):
    u"""
    Jsonでデータをシリアライズし、DBに保存するためのフィールド

    なぜ Json か? ::

    - レコードを人が読める
    - DBで検索もなんとかできる
    - マスターデータもエクセルで人が書くことができる

    注意事項

    - リストや辞書などの簡単なデータ構造しか保持できません
    - 文字列のみを格納することができません。
      文字列は型比較の際に、「エンコードされたJson文字列」として扱うためです。
      ['spam'] のような、リストなどにすれば格納できます。

    例::

        class HamModel(models.Model):

            extra_data = JsonDataField(default={})
    """

    description = u'Jsonでシリアライズするデータフィールド'

    __metaclass__ = models.SubfieldBase  # to_pythonを自動呼び出しするため

    def __init__(self, *args, **kwargs):
        self.add_to_introspection_rule()
        super(JsonDataField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def _deseriarize(self, value):
        if not value:
            return None
        return simplejson.loads(value)

    def to_python(self, value):
        if not type(value) in [str, unicode]:
            return value
        return self._deseriarize(value)

    def get_db_prep_save(self, value, connection):
        if value is None:
            return
        return simplejson.dumps(value)

    def add_to_introspection_rule(self):
        try:
            from south.modelsinspector import add_introspection_rules
        except ImportError:
            pass
        else:
            add_introspection_rules(
                [([JsonDataField], [], {}), ],
                ["^gtoolkit\.db\.fields\.JsonDataField"])
