# -*- coding: utf-8 -*-
"""
テストフィクスチャのリロードテスト
"""
from __future__ import unicode_literals

import unittest
import os


from .models import MockModel


class JsonMasterModelLoadFixtureTest(unittest.TestCase):

    def test_load_test_fixture(self):
        """値の取得のテスト"""
        # テストフィクスチャをリロード
        MockModel.load_test_fixture('jsonmastermodel-testfixture-2.json')
        i = MockModel.objects.get_by_id(3)
        self.assertEqual(i.value, 300)

        # テストフィクスチャをリロード
        MockModel.load_test_fixture('./jsonmastermodel-testfixture.json')
        i = MockModel.objects.get_by_id(2)
        self.assertEqual(i.value, 50)

        # テストフィクスチャを絶対パスでリロード
        MockModel.load_test_fixture(
            os.path.join(
                os.path.abspath(os.path.dirname(__file__)),
                'jsonmastermodel-testfixture-2.json'
            )
        )
        i = MockModel.objects.get_by_id(4)
        self.assertEqual(i.value, 400)
