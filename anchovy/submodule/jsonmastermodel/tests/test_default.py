# -*- coding: utf-8 -*-
"""
継承のテスト
"""
from __future__ import unicode_literals

import unittest

from .models import DefaultValueModel


class JsonMasterModelDefaultTest(unittest.TestCase):

    def test_default_name(self):
        """Nullが入ってた場合のテスト"""
        i = DefaultValueModel.get(1)
        self.assertEqual(i.name, None)  # NoneはNoneとして取得する

    def test_default_no_exists_in_fixture(self):
        """fixture に存在しないフィールドのテスト"""
        i = DefaultValueModel.get(1)
        self.assertEqual(i.no_exists_in_fixture, 100)
