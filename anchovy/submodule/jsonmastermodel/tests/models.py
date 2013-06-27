# -*- coding: utf-8 -*-

import os

from .. import JsonMasterModel, JsonMasterField,\
    JsonMasterIntegerField, JsonMasterCharField, JsonMasterTextField
from jsonmastermodel.fields import JsonMasterBooleanField


class MockModel(JsonMasterModel):
    MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture.json' % \
                            os.path.dirname(__file__)

    name = JsonMasterCharField()
    value = JsonMasterIntegerField()
    detail_text = JsonMasterTextField()


class MockLargeModel(JsonMasterModel):
    MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture-large.json' % \
                            os.path.dirname(__file__)

    category = JsonMasterCharField()
    value = JsonMasterIntegerField()
    detail_text = JsonMasterTextField()


class ChildMockModel(MockModel):
    MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture.json' % \
                            os.path.dirname(__file__)


class DefaultValueModel(JsonMasterModel):
    MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture-with-null.json' % \
                            os.path.dirname(__file__)

    name = JsonMasterCharField(default='default_name')
    no_exists_in_fixture = JsonMasterIntegerField(default=100)


class BaseFailMockModel(JsonMasterModel):
    """
    失敗テスト用
    """
    MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture.json' % \
                            os.path.dirname(__file__)


class NameFailMockModel(BaseFailMockModel):
    name = JsonMasterIntegerField()  # テストのための間違った指定


class ValueFailMockModel(BaseFailMockModel):
    # テストのための間違った指定、ただしこれは str で取得できる
    value = JsonMasterCharField()


class DetailFailMockModel(BaseFailMockModel):
    detail_text = JsonMasterBooleanField()  # テストのための間違った指定
