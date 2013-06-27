# -*- coding: utf-8 -*-
"""
auth_device api
"""
from gsocial.set_container import containername

from base import AuthDeviceManager
from error import AuthDeviceError

def get_auth_device_api(request, **argv):
    """
    端末認証APIの取得
    """
    func = API_CALL_TABLE.get(containername, None)
    if not func:
        raise AuthDeviceError('Not supported plathome (%s)' % str(containername))

    return func(request, **argv)

def get_api_gree(request, **argv):
    """
    端末認証マネージャ(GREE)の取得
    """
    import gree
    return AuthDeviceManager(request, gree.AuthAPIGree, **argv)

# プラットフォームごとのインスタンスを返す関数の定義
API_CALL_TABLE = {
    'gree': get_api_gree,
}
