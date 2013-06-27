# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import six
import json
import datetime

from django.utils.encoding import smart_text
from django.utils import dateparse

from .exceptions import ValidationError


class NOT_PROVIDED:
    """
    Field の デフォルトの default 値。None とも区別するために使う
    """
    pass


class JsonMasterField(object):
    """
    JsonMasterModelようのField
    score = JsonMasterField(default=0) みたいに使う。

    :param default: 値を取得時、無かった場合と None だった場合のデフォルト値
    :param verbose_name: Django モデルフィールドの verbose_name の代用。
        指定はできるが内部では使っていないので、指定しても意味ない
    """

    def __init__(self, verbose_name=None, default=NOT_PROVIDED):
        self._verbose_name = verbose_name
        self._default = default

    def _to_python(self, value):
        """
        Json の dict から モデルフィールドにするとき通る。

        django Model の、clean(), validate(), to_python() の処理を
        ここで行う
        """
        return value

    def _get_value_from_fixture_record_fields(
            self, fixture_record_fields, field_name):
        """
        fixture の fields の辞書から、実際に使う値を取得
        """
        if self._default is not NOT_PROVIDED:
            # default が指定してあれば、その値を使う
            json_value = fixture_record_fields.get(
                field_name, self._default)
        else:
            # 値がなければ KeyError を raise
            json_value = fixture_record_fields[field_name]
        return self._to_python(json_value)


class JsonMasterIntegerField(JsonMasterField):
    """
    値が int であることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValidationError(value)


class JsonMasterFloatField(JsonMasterField):
    """
    値が float であることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValidationError(value)


class JsonMasterNullBooleanField(JsonMasterField):
    """
    値が bool か null であることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        if value in (True, False):
            return bool(value)
        if value in ('None',):
            return None
        if value in ('t', 'True', '1'):
            return True
        if value in ('f', 'False', '0'):
            return False
        raise ValidationError(value)


class JsonMasterBooleanField(JsonMasterField):
    """
    値が bool であることを保証するフィールド
    """

    def _to_python(self, value):
        if value in (True, False):
            return bool(value)
        if value in ('t', 'True', '1'):
            return True
        if value in ('f', 'False', '0'):
            return False
        raise ValidationError(value)


class JsonMasterTextField(JsonMasterField):
    """
    値が文字列であることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        if isinstance(value, six.string_types):
            return value
        return smart_text(value)


class JsonMasterCharField(JsonMasterTextField):
    """
    値が文字列であることを保証するフィールド

    実装は JsonMasterTextField と同じ。
    比較的短い文字列で使う。
    max_length の考慮など必要なら行う
    """
    pass


class JsonMasterDateTimeField(JsonMasterField):
    """
    値が datetime あることを保証するフィールド
    """
    def _to_python(self, value):
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, six.string_types):
            return dateparse.parse_datetime(value)
        if isinstance(value, (tuple, list)):
            return datetime.datetime(*value)
        raise ValidationError(value)


class JsonMasterDateField(JsonMasterField):
    """
    値が date あることを保証するフィールド
    """
    def _to_python(self, value):
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, six.string_types):
            return dateparse.parse_date(value)
        if isinstance(value, (tuple, list)):
            return datetime.date(*value)
        raise ValidationError(value)


class JsonMasterDictField(JsonMasterField):
    """
    値が dict あることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        if isinstance(value, dict):
            return value
        # raises IndentationError, TypeError
        return dict(value)


class JsonMasterTupleField(JsonMasterField):
    """
    値が tuple あることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        if isinstance(value, tuple):
            return value
        # raises IndentationError, TypeError
        return tuple(value)


class JsonMasterJsonField(JsonMasterField):
    """
    値が json あることを保証するフィールド
    """

    def _to_python(self, value):
        if value is None:
            return None
        if isinstance(value, six.string_types):
            return json.loads(value)
        return ValidationError(value)

# こんなのもあると便利かも
# JsonMasterOrderedDictField
# JsonMasterNamedTupleField
