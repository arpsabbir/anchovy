# -*- coding: utf-8 -*-

import unittest

from django.db import models
from models import HorizontalPartitioningModel
from transaction import MultipleTransaction, MultipleTransactionXA

class HorizontalPartitioningMock(HorizontalPartitioningModel):
    player_id = models.CharField(max_length=255, db_index=True)
    value = models.TextField()
    class Meta:
        pass

class TestModel(unittest.TestCase):

    def test_horizontal_partitioning_model(self):
        """
        インスタンスのテスト
        """
        from __init__ import HorizontalPartitioningMixin
        hpm = HorizontalPartitioningMock.objects.partition(u'test01').create(
            player_id=u'test01', value=u'spam-eggs')
        # フィールドが継承されているかのテスト
        self.assertEqual(hpm.HORIZONTAL_PARTITIONING_KEY_FIELD,
            HorizontalPartitioningMixin.HORIZONTAL_PARTITIONING_KEY_FIELD)
        self.assertGreaterEqual(hpm.horizontal_partitioning_database_name, 0)
        inst = HorizontalPartitioningMock.objects.partition(u'test01').get(player_id=u'test01')
        self.assertEqual(inst.value, u'spam-eggs')

    def test_horizontal_partitioning_model_class(self):
        """
        クラスメソッド(マネージャー)のテスト
        """
        self.assertTrue(type(HorizontalPartitioningMock.objects.all_partitions()), 'generator')
        self.assertTrue(isinstance(HorizontalPartitioningMock.objects.partition(u'test01'),
            models.query.QuerySet))
        self.assertTrue(isinstance(HorizontalPartitioningMock.objects.all_partition_count(), (int, long,)))

    def test_multipletransaction(self):
        from django.conf import settings
        from __init__ import get_horizontal_partitioning_database_name
        if settings.DATABASES['default']['ENGINE'].endswith('.sqlite3'):
            return # skip because sqlite3
        db_name = get_horizontal_partitioning_database_name('test02')
        if settings.DATABASES[db_name]['ENGINE'].endswith('.sqlite3'):
            return # skip because sqlite3
        mt = MultipleTransaction(db_names=['default',], user_ids=['test02',])
        hpm = HorizontalPartitioningMock()
        hpm.player_id = u'test02'
        hpm.value = u'The quick brown fox'
        hpm.save()
        mt.commit()