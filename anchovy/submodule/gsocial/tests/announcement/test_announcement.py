# -*- coding: utf-8 -*-
"""
gsocial/utils/authdevice/base.py テスト
"""
import mock
import unittest
from django.utils import timezone
from gsocial.utils.announcement import AnnouncementGree

class TestAnnouncementGree(unittest.TestCase):

    def test_create(self):
        """
        AnnouncementGree の生成テスト
        """
        # Requestまわりはテストできる状態じゃないので
        ag = AnnouncementGree(mock.Mock())
        self.assertTrue(ag)

    def test__get_id_from_result(self):
        ag = AnnouncementGree(mock.Mock())
        result = '{"entry":[{"id":"201210_86"}]}'
        self.assertEqual(ag._get_id_from_result(result), '201210_86')

    def test__create_data_dict(self):
        ag = AnnouncementGree(mock.Mock())
        result = ag._create_data_dict(title=u'こんにちは', body=u'世界')
        self.assertEqual(result['messages']['ja-Jpan-JP']['title'], u'こんにちは')
        self.assertEqual(result['messages']['ja-Jpan-JP']['body'], u'世界')
        self.assertEqual(result['devices'], ag.DEFAULT_DEVICES)
        self.assertEqual(result['images'], ag.DEFAULT_IMAGES)
        self.assertEqual(result['url'], ag.DEFAULT_URL)
        self.assertEqual(result['attr'], ag.DEFAULT_ATTR)
        self.assertEqual(result['country'], ag.DEFAULT_COUNTRY)
        self.assertIsNone(result['start_time'])

        ag = AnnouncementGree(mock.Mock())
        result = ag._create_data_dict(title=u'こんにちは', body=u'世界',
            id='test-id', devices=['spweb'], images=['http://example.com/test.png'],
            url='http://example.com/',
            attr={'key':'value',}, country=['JP'],
            start_datetime_utc=timezone.now(),
            force_str=True)
        self.assertEqual(result['messages']['ja-Jpan-JP']['title'], 'こんにちは')
        self.assertEqual(result['messages']['ja-Jpan-JP']['body'], '世界')
        self.assertEqual(result['id'], 'test-id')
        self.assertEqual(result['devices'][0], 'spweb')
        self.assertEqual(result['images'][0], 'http://example.com/test.png')
        self.assertEqual(result['url'], 'http://example.com/')
        self.assertEqual(result['attr']['key'], 'value')
        self.assertEqual(result['country'][0], 'JP')
        self.assertIsNotNone(result['start_time'])
