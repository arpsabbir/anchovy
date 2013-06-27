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
from __future__ import unicode_literals
import logging
import unittest

from gtoolkit.time.elapsed_time_watch import ElapsedTimeWatch
from .models import MockLargeModel


logger = logging.getLogger('JsonMasterModel')


class LargeJsonMasterModelTest(unittest.TestCase):

    def get_mock_model(self):
        """
        テスト時のみ、 MockModelを評価して作る。
        cached_property にすると、テストコード評価時に動作してしまうので、
        memoized_property にしている。
        """
        etw = ElapsedTimeWatch()

        model = MockLargeModel
        logger.debug('MockLargeModel new. elapsed: {} ms'
                     .format(etw.elapsed_time_ms))
        model.objects.all()
        # MacBookAir ローカル環境だと、10000レコード読み込みで 110ms
        logger.debug('MockLargeModel create. elapsed: {} ms'
                     .format(etw.elapsed_time_ms))
        return model

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
        m.objects.filter(category='category-50')
        # test_quick_filter の暖気と同様の処理
        # test_objects_filter standby elapsed: 23 ms
        # 1回だけならこちらが早い
        logger.debug('test_objects_filter standby elapsed: {} ms'
                     .format(etw.elapsed_time_lap_ms))
        for category_number in [10, 20, 30, 40, 50, 60, 70]:
            category = 'category-{}'.format(category_number)
            L = m.objects.filter(category=category)
            self.assertEqual(len(L), 100)
        # test_objects_filter elapsed: 169 ms
        logger.debug('test_objects_filter elapsed: {} ms'
                     .format(etw.elapsed_time_lap_ms))

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
        m.quick_filter(category='category-50')  # 暖気しておく
        # 暖気はけっこう時間かかる
        # quick_filter standby elapsed: 119 ms
        logger.debug('quick_filter standby elapsed: {} ms'
                     .format(etw.elapsed_time_lap_ms))
        for category_number in [10, 20, 30, 40, 50, 60, 70]:
            category = 'category-{}'.format(category_number)
            L = m.quick_filter(category=category)
            self.assertEqual(len(L), 100)
        # ただし、一度キャッシュに乗ってしまえば早い
        # quick_filter elapsed: 0 ms
        logger.debug('quick_filter elapsed: {} ms'
                     .format(etw.elapsed_time_lap_ms))

    def test_quick_filter_different_object(self):
        """
        quick_filter が違うオブジェクトを返すテスト
        """
        try:
            m = self.get_mock_model()
        except IOError as e:
            # テストフィクスチャなければキャンセル
            logger.debug('LargeJsonMasterModelTest: test cancel. {}'
                         .format(str(e)))
            return
        o1 = m.quick_filter(category='category-60')[0]
        o2 = m.quick_filter(category='category-60')[0]
        self.assertEqual(o1.id, o2.id)  # 内容は同じだけど
        self.assertIsNot(o1, o2)  # 違うインスタンス
