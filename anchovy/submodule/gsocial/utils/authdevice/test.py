# -*- coding: utf-8 -*-

# 端末認証テスト

from gsocial.log import Log
from gsocial.utils.authdevice.api import get_auth_device_api

def TEST(request, user_id=None):
    # API取得
    authdevice = get_auth_device_api(request, user_id=user_id)
    # 認証済みか
    if authdevice.is_auth_device:
        Log.debug('Device authrized already. id=%s' % authdevice.auth_id)
    else:
        # 認証済みでなければチェック
        Log.debug('Checking device auth')
        is_auth_done = authdevice.check_auth_device()
        if is_auth_done:
            # 認証処理完了
            Log.debug('Device authrized now. id=%s' % authdevice.auth_id)
