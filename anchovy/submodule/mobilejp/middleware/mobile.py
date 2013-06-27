# -*- coding: utf-8 -*-
from uamobile import detect, Context
from uamobile.docomo import DoCoMoUserAgent
from uamobile.factory.docomo import DoCoMoUserAgentFactory
from uamobile.softbank import SoftBankUserAgent
from uamobile.factory.softbank import SoftBankUserAgentFactory

from mobilejp.utils.device import MobileDevice
from django.conf import settings

__all__ = ['get_current_device', 'get_current_request', 'UserAgentMobileMiddleware', 'context']

try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()

def get_current_device():
    return getattr(_thread_locals, 'device', None)

def get_is_webview():
    device = getattr(_thread_locals, 'device', None)
    if device:
    	return device.is_webview
    else:
	return False


def get_current_request():
    return getattr(_thread_locals, 'request', None)

class UserAgentMobileMiddleware(object):
    context = Context()

    def process_request(self, request):
        request.device = detect(request.META, self.context)
        _thread_locals.request = request
        _thread_locals.device  = request.device


class UserAgentMobile2Middleware(object):
    """
    端末認証を改良したミドルウェア
    deviceでスマートフォンかどうかもの識別できるようにしたもの
    """
    context = Context()

    def process_request(self, request):

        device = MobileDevice(request, self.context)
        request.device = device

        _thread_locals.request = request
        _thread_locals.device  = request.device

