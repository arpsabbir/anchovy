# -*- coding: utf-8 -*-
"""
gsocial/utils/authdevice/base.py テスト
"""
from nose.tools import eq_, ok_

from gsocial.utils.authdevice.base import AuthRecord, AuthAPI, AuthDeviceManager


class Test_AuthRecord():

    # TODO : テストできない
    def test_cache_key(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test_get_record(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test_create_record(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test_update_record(self):
        """
        test
        """
        ok_(True)


class Test_AuthAPI():

    # TODO : テストできない
    def test_cache_key(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test_get_auth_id(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test__get_auth_id(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test_user_grade_cache_key(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test_get_auth(self):
        """
        test
        """
        ok_(True)

    # TODO : テストできない
    def test__get_auth(self):
        """
        test
        """
        ok_(True)


class Test_AuthDeviceManager():

    def test_check_user_grade(self):
        """
        test
        """
        check_user_grade = AuthDeviceManager.check_user_grade("2")
        eq_(check_user_grade, False)
        check_user_grade = AuthDeviceManager.check_user_grade("1")
        eq_(check_user_grade, False)
        check_user_grade = AuthDeviceManager.check_user_grade("3")
        eq_(check_user_grade, True)


