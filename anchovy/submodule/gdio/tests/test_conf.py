# -*- coding: utf-8 -*-
"""
gdio.conf のテスト
"""

import unittest
import os

from gdio.conf import gDIOSettings

def can_import_django_settings():
    try:
        import django.conf.settings
        return True
    except ImportError:
        return False

class TestSettings(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")

    @unittest.skipIf(can_import_django_settings(),
                         'can import django.conf.settings')
    def test_default_conf(self):
        settings = gDIOSettings()
        self.assertEqual(settings.KEY_PREFIX, '')
        self.assertEqual(settings.DB, 'default')


    @unittest.skipUnless(can_import_django_settings(),
                     'can not import django.conf.settings')
    def test_conf(self):
        settings = gDIOSettings()
        self.assertEqual(settings.KEY_PREFIX, 'spam')
        self.assertEqual(settings.DB, 'ham')
