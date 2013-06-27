# -*- coding:utf-8 -*-
"""
auth device decorator
"""
from functools import wraps
from django.core.urlresolvers import reverse
from gsocial.http import HttpResponseOpensocialRedirect
from gsocial.utils.authdevice.api import get_auth_device_api

# エラークラス
class Error(Exception):
    """
    error
    """
    pass

def require_authdevice(error_view_name=None, error_view_params=None):
    """
    端末認証されてないのなら例外発生かリダイレクトするデコレータ
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwds):
            # API取得
            authdevice = get_auth_device_api(request)
            # 認証済みか
            if not authdevice.is_auth_device:
                if error_view_name:
                    # error_view_nameが指定されていればリダイレクトする
                    args = error_view_params if error_view_params else []
                    view = reverse(error_view_name, args=args)
                    return HttpResponseOpensocialRedirect(view)
                else:
                    # error_view_nameが指定されていなければ例外発生
                    err_mes = 'Not authorized device (UserID:%s)'
                    raise Error(err_mes % request.osuser.userid)

            return view_func(request, *args, **kwds)
        return _wrapped_view
    return decorator

# サンプルコード
'''
@require_osuser
@require_authdevice(error_view_name='home')
def sample_view(request):
    ......
'''
