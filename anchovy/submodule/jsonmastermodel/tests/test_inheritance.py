# -*- coding: utf-8 -*-
"""
継承のテスト
"""
from __future__ import unicode_literals

import unittest

from .models import ChildMockModel


class JsonMasterModelTest(unittest.TestCase):

    def get_mock_model(self):
        return ChildMockModel

    def test_attr_int(self):
        """値の取得のテスト"""
        m = self.get_mock_model()
        i = m.objects.get_by_id(1)
        self.assertEqual(i.value, 200)