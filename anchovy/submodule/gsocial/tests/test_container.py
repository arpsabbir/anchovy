# -*- coding: utf-8 -*-
from nose.tools import eq_

from django.test import TestCase
from gsocial.utils.base import GsocialCache
from django.template import loader
from django.conf import settings

from gsocial.set_container import *

class TestContainer(TestCase):
    """
    Containerテスト
    """

    def test__init__(self):
        """
        test__init__
        """
        Container()

    def test_name(self):
        """
        self.name test
        """
        eq_(Container().name, "gree")

    def test_payment_success_status(self):
        """
        self.payment_success_status test
        """
        eq_(Container().payment_success_status, "2")

    def test_payment_cancel_status(self):
        """
        self.payment_cancel_status test
        """
        eq_(Container().payment_cancel_status, "3")

    def test_payment_template(self):
        """
        payment template
        """
        tmp = loader.get_template('opensocial/payment/'+ Container().container['payment_info_template'])
#        eq_(Container().payment_template(), tmp.render)
        eq_(Container().payment_template().__class__, tmp.__class__)

    def test_monthly_payment_template(self):
        """
        monthly payment template
        """
        tmp = loader.get_template('opensocial/monthly_payment/'+ Container().container['payment_info_template'])
        eq_(Container().monthly_payment_template.__class__, tmp.__class__)

    def test_get_token(self):
        """
        test
        """
        eq_(Container().get_token(), None)

    def test_oauth_request(self):
        """
        test
        """

        method = "DEBUG"
        requestor_id = 1111
        path = "ggg"
        tmp_request =  Container().oauth_request(method, requestor_id, path)
        assert(tmp_request !=  None)

    def test_encode_emoji(self):
        """
        TODO: 文字列コードをcheckすべき
        """
        text = "っっっっｇ"
        encode_text = "\xe3\x81\xa3\xe3\x81\xa3\xe3\x81\xa3\xe3\x81\xa3\xef\xbd\x87"
        assert(Container().encode_emoji(text)  ==  encode_text)

    def test_decode_emoji(self):
        """
        test
        """
        text = "\xe3\x81\xa3\xe3\x81\xa3\xe3\x81\xa3\xe3\x81\xa3\xef\xbd\x87"
        decode_text = "っっっっｇ"
        assert(Container().decode_emoji(text)  ==  decode_text)


class TestResponseError(TestCase):
    """
    レスポンスエラーテスト
    """
    def test__init__(self):
        """
        初期化テスト
        """
        Container.ResponseError()

    def test__str__(self):
        """
        __str__テスト
        """
        assert(Container.ResponseError().__str__() != None)

    def test_dump(self):
        """
        test
        """
        assert(Container.ResponseError().dump() != None)


class Test_GrobalModule(TestCase):
    """
    test
    """
    def test_get_containerdata(self):
        """
        test
        """
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../container_list.yaml"
        data = yaml.load(open(file_path).read())
        container = data[settings.OPENSOCIAL_CONTAINER]
        eq_(get_containerdata()['container'], container['container'])
        eq_(containerdata['container'], container['container'])

    def test_get_containername(self):
        """
        test
        """
        file_path = os.path.dirname(os.path.abspath(__file__)) + "/../container_list.yaml"
        data = yaml.load(open(file_path).read())
        container = data[settings.OPENSOCIAL_CONTAINER]
        eq_(get_containername(), container['container'])
        eq_(containername, container['container'])
