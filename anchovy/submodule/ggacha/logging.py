# -*- coding: utf-8 -*-
"""
ggacha.logic 配下のクラスに, ログ関連の機能を提供する.
"""
from ggacha.utils import NullContext

class LoggingMixin(object):
    """
    ログ関連の機能を追加する Mix-in クラス.

    現在は kome 専用.
    """
    class _Logging(object):
        def get_null_context(self):
            return NullContext()

        def get_logger(self, logging_kwargs):
            if logging_kwargs is None:
                return self.get_null_context()

            try:
                from django.conf import settings
                from kome.core.sender import Sender
                from kome.middleware.actionlog import ActionLogger

                config = settings.KOME_INFO['config']
                return ActionLogger(Sender(config), **logging_kwargs)
            except:
                return self.get_null_context()

        def get_args(self, request):
            if not hasattr(request, 'action_logger'):
                return None

            try:
                from kome.middleware.actionlog import log
            except ImportError:
                return None

            return {'userid': request.action_logger.uid,
                    'devicename': request.action_logger.device,
                    'parent': log().actname,
                    'parentid': log().id}


    @property
    def logging(self):
        if hasattr(self, '_logging'):
            return self._logging

        self._logging = self._Logging()
        return self._logging
