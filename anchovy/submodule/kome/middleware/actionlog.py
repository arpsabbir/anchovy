# coding: utf-8

import re
from uamobile import detect, Context
from kome.core.types import DeviceType
from kome.core.sender import Sender
from kome.middleware import _settings
from kome.middleware._log import log
from kome.middleware.action_logger import ActionLogger
from kome.middleware.decorator import deco
from kome.middleware._util import ignore_exception_if_no_debug

_null_sender = Sender({'type': 'null'})
_init_osuserid = 'opensocial_viewer_id'
sender = _null_sender
osuserid = _init_osuserid

# regex
_IOS_RE = re.compile(r'iPhone|iPad|iPod')
_ANDROID_RE = re.compile(r'Android')

def to_device_name(META):
    device = detect(META)
    if device.is_nonmobile():
        ua = META.get('HTTP_USER_AGENT', '')
        if _IOS_RE.search(ua):
            return DeviceType.SP_iPhone
        elif _ANDROID_RE.search(ua):
            return DeviceType.SP_Android
        else:
            return DeviceType.Unknown
    else:
        return DeviceType.FP


class ActionLogMiddleware(object):
    context = Context()

    def __init__(self):
        global sender
        global osuserid
        config = _settings.get_config()
        if config is not None:
            sender = Sender(config)
        else:
            sender = _null_sender
        id = _settings.get_osuserid()
        if id is not None:
            osuserid = id
        else:
            osuserid = _init_osuserid

    def process_request(self, request):
        return ignore_exception_if_no_debug(
            lambda: self._process_request(request))

    def _process_request(self, request):
        global osuserid
        # ユーザIDが無い
        if not hasattr(request, osuserid):
            return

        global sender
        devicename = to_device_name(request.META)
        userid = request.opensocial_viewer_id
        request.action_logger = ActionLogger(sender, userid, devicename)
        request.action_logger.begin()

    def process_response(self, request, response):
        return ignore_exception_if_no_debug(
            lambda: self._process_response(request, response), response)

    def _process_response(self, request, response):
        # process_request が呼ばれていない
        if not hasattr(request, 'action_logger'):
            return response

        # ログ出力
        request.action_logger.flush()

        return response

action_log_decorator_initialized = False
def action_log_decorator(func):
    global sender
    global osuserid
    global action_log_decorator_initialized
    if not action_log_decorator_initialized:
        action_log_decorator_initialized = True
        config = _settings.get_config()
        if config is not None:
            sender = Sender(config)
        else:
            sender = _null_sender
        id = _settings.get_osuserid()
        if id is not None:
            osuserid = id
        else:
            osuserid = _init_osuserid

    from functools import wraps
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        devicename = to_device_name(request.META)
        with ActionLogger(sender, getattr(request, osuserid), devicename):
            return func(request, *args, **kwargs)
    return wrapper
