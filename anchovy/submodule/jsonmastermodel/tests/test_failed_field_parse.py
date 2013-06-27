# -*- coding: utf-8 -*-
"""
フィールドのパースを失敗させるテスト
"""
from __future__ import unicode_literals

import unittest

from ..exceptions import ValidationError
from .models import NameFailMockModel, ValueFailMockModel, DetailFailMockModel


class JsonMasterModelFieldParseTest(unittest.TestCase):

    def test_name_fail(self):
        """
        name フィールドは int じゃないのでエラーになるのテスト
        """
        with self.assertRaises(ValidationError):
            NameFailMockModel.get(2)

    def test_value_fail(self):
        """
        value フィールドには数字が入っているが、
        Char フィールドに指定されている。
        その場合、数値が str として取得される
        """
        i = ValueFailMockModel.get(2)
        self.assertEqual(i.value, '50')

    def test_detail_fail(self):
        """
        detail フィールドは BooleanFieldじゃない
        """
        with self.assertRaises(ValidationError):
            DetailFailMockModel.get(2)