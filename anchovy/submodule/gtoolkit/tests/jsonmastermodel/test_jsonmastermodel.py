# -*- coding: utf-8 -*-
"""
django-nose を使う場合のテスト方法::

    ./manage.py test gtoolkit.tests.test_jsonmastermodel --settings=... --noinput
"""

import unittest
import os

from gtoolkit.db import JsonMasterModel


class JsonMasterModelTest(unittest.TestCase):

    def get_mock_model(self):
        """
        テスト時のみ、 MockModelを評価して作る。
        cached_property にすると、テストコード評価時に動作してしまうので、
        memoized_property にしている。
        """
        class MockModel(JsonMasterModel):
            MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture.json' %\
                                    os.path.dirname(__file__)
        return MockModel

    def test_attr_int(self):
        """値の取得のテスト"""
        m = self.get_mock_model()
        i = m.objects.get_by_id(1)
        self.assertEqual(i.value, 200)

    def test_attr_unicode(self):
        """unicode値が取得できるかのテスト"""
        m = self.get_mock_model()
        i = m.objects.get(id=2)
        self.assertEqual(i.name, u'ﾌｫｰｽﾛｯﾄﾞ')

    def test_doesnotexist(self):
        """get_by_id, get で該当なしの時 Raise されるか"""
        m = self.get_mock_model()
        with self.assertRaises(m.DoesNotExist):
            m.objects.get_by_id(3)
        with self.assertRaises(m.DoesNotExist):
            m.objects.get(id=3)

    def test_all(self):
        """objects.all()のテスト"""
        m = self.get_mock_model()
        all_ = m.objects.all()
        self.assertEqual(len(all_), 2)

    def test_filter(self):
        """objects.filter()のテスト"""
        m = self.get_mock_model()
        filterd = m.objects.filter(value=50)
        self.assertEqual(len(filterd), 1)
        self.assertEqual(filterd[0].id, 2)

    def test_get(self):
        m = self.get_mock_model()
        i = m.get(2)
        self.assertEqual(i.name, u'ﾌｫｰｽﾛｯﾄﾞ')

    def test_get_all(self):
        m = self.get_mock_model()
        all_ = m.get_all()
        self.assertEqual(len(all_), 2)

    def test_get_field_dict(self):
        m = self.get_mock_model()
        d = m.get_field_dict('value')
        self.assertIn(200, d)
        self.assertIn(50, d)
        self.assertEqual(d[200].name, u'ｷｭｱﾛｯﾄﾞ')

    def test_get_field_list_dict(self):
        m = self.get_mock_model()
        d = m.get_field_list_dict('name')
        self.assertIn(u'ｷｭｱﾛｯﾄﾞ', d)
        self.assertIn(u'ﾌｫｰｽﾛｯﾄﾞ', d)
        self.assertIsInstance(d[u'ﾌｫｰｽﾛｯﾄﾞ'], list)
        self.assertEqual(len(d[u'ﾌｫｰｽﾛｯﾄﾞ']), 1)
        self.assertEqual(d[u'ﾌｫｰｽﾛｯﾄﾞ'][0].value, 50)
