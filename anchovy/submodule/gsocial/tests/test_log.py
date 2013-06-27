# -*- coding: utf-8 -*-
import unittest
from nose.tools import eq_, ok_

from gsocial.log import Log

class TestLog(unittest.TestCase):

    def test_get_logging_res(self):
        msg = 'Simplejson Error.'
        obj = 'hoge'
        res1, res2, res3 = Log._get_logging_res(msg, obj)

        ex_format_msg1 = '----- START [ File:case.py(318), Method:run ] -----'
        ex_format_msg2 = '"Simplejson Error.", hoge'
        ex_format_msg3 = '----- END [ File:case.py(318), Method:run ]   -----'

        eq_(ex_format_msg1, res1)
        eq_(ex_format_msg2, res2)
        eq_(ex_format_msg3, res3)

    def test_debug(self):
        """
        関数が問題なく通るかのみ確認
        """
        msg = 'Simplejson Error1.'
        obj = 'hoge'
        Log.debug(msg, obj)

    def test_info(self):
        """
        関数が問題なく通るかのみ確認
        """
        msg = 'Simplejson Error2.'
        obj = 'hoge'
        Log.info(msg, obj)

    def test_error(self):
        """
        関数が問題なく通るかのみ確認
        """
        msg = 'Simplejson Error3.'
        obj = 'hoge'
        Log.info(msg, obj)

    def test_warn(self):
        """
        関数が問題なく通るかのみ確認
        """
        msg = 'Simplejson Error4.'
        obj = 'hoge'
        Log.info(msg, obj)

