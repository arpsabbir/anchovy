# -*- coding: utf-8 -*-

import unittest

from gtoolkit.db import UniqueIDFieldMixin

class TestDb(unittest.TestCase):

    def test_uniqueidfield(self):
        instance = UniqueIDFieldMixin()
        uuid = instance._meta.fields[0].pre_save(instance, True)
        sample = instance._meta.fields[0].generator()
        self.assertGreater(len(sample), 10)

        self.assertEqual(len(uuid), len(sample))
        self.assertEqual(len(instance.unique_id), len(sample))

        instance2 = UniqueIDFieldMixin()
        uuid2 = instance2._meta.fields[0].pre_save(instance2, True)
        self.assertNotEqual(uuid, uuid2) #違う値になる。

        uuid3 = instance2._meta.fields[0].pre_save(instance2, False)
        self.assertEqual(instance2.unique_id, uuid2) #変化しない
        self.assertEqual(uuid3, uuid2) #変化しない


    def test_uniqueidfield_set_manually(self):
        instance = UniqueIDFieldMixin()
        instance.unique_id = 'set-manually'
        uuid = instance._meta.fields[0].pre_save(instance, True)
        self.assertEqual(uuid, 'set-manually')
        self.assertEqual(instance.unique_id, 'set-manually')
