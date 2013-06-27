# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_, ok_

from gsocial.utils.activity.base import ActivityBase


class ActivityBaseTests(unittest.TestCase):

    def test_send(self):
        target = ActivityBase()
        value = target.send(userid='10000', title='リクエストテスト')
        eq_(None, value)

