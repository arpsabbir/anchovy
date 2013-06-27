# -*- coding: utf-8 -*-

from django.test import TestCase

from django.db import models

from gtoolkit.db.fields import JsonDataField

class SampleJsonFieldModel(models.Model):

    class Meta:
        app_label = 'quest'

    spam_field = models.TextField()
    extra_data = JsonDataField(null=True)


class SampleJsonFieldDefaultModel(models.Model):

    class Meta:
        app_label = 'quest'

    spam_field = models.TextField()
    extra_data = JsonDataField(default=[])


class JsonFieldModelTest(TestCase):

    def test_save(self):
        sample = SampleJsonFieldModel()
        sample.spam_field = 'ham'
        sample.save()
        sample = list(SampleJsonFieldModel.objects.order_by('-id'))[-1]
        self.assertEqual(sample.spam_field, 'ham')

    def test_extradata_save(self):
        sample = SampleJsonFieldModel(spam_field='ham2')
        sample.extra_data = {
            'a': 100,
            'b': 200,
        }
        sample.save()
        sample = list(SampleJsonFieldModel.objects.order_by('-id'))[-1]
        self.assertEqual(sample.extra_data['a'], 100)
        self.assertEqual(sample.extra_data['b'], 200)


class JsonFieldModelDefaultTest(TestCase):

    def test_save(self):
        sample = SampleJsonFieldDefaultModel()
        self.assertIsInstance(sample.extra_data, list)
        sample.spam_field = u'eggs'
        sample.save()
        record_id = sample.id

        sample = SampleJsonFieldDefaultModel.objects.get(id=record_id)
        self.assertIsInstance(sample.extra_data, list)
        sample.extra_data.append('a')
        sample.extra_data.append('b')
        sample.save()

        sample = SampleJsonFieldDefaultModel.objects.get(id=record_id)
        self.assertEqual(len(sample.extra_data), 2)
        self.assertEqual(sample.extra_data[1], 'b')

        sample = SampleJsonFieldDefaultModel()
        self.assertEqual(len(sample.extra_data), 0) #共有メモリを使ってないか