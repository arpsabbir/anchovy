# -*- coding: utf-8 -*-
"""

大サイズの JsonMasterModel のテスト

jsonmastermodel-testfixture-large.json が無いとテストできません。
作るには、 ./create_testfixture.py を実行してください。
2MBぐらいの Json ファイルができます


結果::

    * .objects.filter を使った場合: 125 ms
    * .quick_filter を使った場合: 6 ms

"""
import logging
import unittest
import os

from gtoolkit.db import JsonMasterModel
from gtoolkit.time.elapsed_time_watch import ElapsedTimeWatch

logger = logging.getLogger('JsonMasterModel')


class LargeJsonMasterModelTest(unittest.TestCase):

    def get_mock_model(self):
        """
        テスト時のみ、 MockModelを評価して作る。
        cached_property にすると、テストコード評価時に動作してしまうので、
        memoized_property にしている。
        """
        etw = ElapsedTimeWatch()

        class MockModel(JsonMasterModel):
            MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture-large.json' %\
                                    os.path.dirname(__file__)

        # MacBookAir ローカル環境だと、10000レコード読み込みで 110ms
        logger.debug('Mockmodel create. elapsed: {} ms'
                     .format(etw.elapsed_time_ms))

        return MockModel

    def test_objects_filter(self):
        """
        MockModel.objects.filter のテスト

        test_objects_filter elapsed: 125 ms
        """
        try:
            m = self.get_mock_model()
        except IOError as e:
            # テストフィクスチャなければキャンセル
            logger.debug('LargeJsonMasterModelTest: test cancel. {}'
                         .format(str(e)))
            return
        etw = ElapsedTimeWatch()

        for category_number in [10, 20, 30, 40, 50, 60, 70]:
            category = 'category-{}'.format(category_number)
            L = m.objects.filter(category=category)
            self.assertEqual(len(L), 100)

        logger.debug('test_objects_filter elapsed: {} ms'
                     .format(etw.elapsed_time_ms))

    def test_quick_filter(self):
        """
        MockModel.quick_filter のテスト
        objects.filter より早い

        quick_filter elapsed: 6 ms
        """
        try:
            m = self.get_mock_model()
        except IOError as e:
            # テストフィクスチャなければキャンセル
            logger.debug('LargeJsonMasterModelTest: test cancel. {}'
                         .format(str(e)))
            return
        etw = ElapsedTimeWatch()

        for category_number in [10, 20, 30, 40, 50, 60, 70]:
            category = 'category-{}'.format(category_number)
            L = m.quick_filter(category=category)
            self.assertEqual(len(L), 100)
            #logger.debug(','.join([str(i.id) for i in L]))
        logger.debug('quick_filter elapsed: {} ms'
                     .format(etw.elapsed_time_ms))
