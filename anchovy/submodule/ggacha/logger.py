# -*- coding: utf-8 -*-
"""
ログ関連の機能を提供する.

logging.py と紛らわしいが, こちらは python 標準の logging 専用.

Django Settings の LOGGING に 'ggacha' を追加する事.
"""
from __future__ import absolute_import
import sys
import traceback
import threading
import logging

class WritableLogMixin(object):
    """
    ログ関連の機能を追加する Mix-in クラス.
    """
    @property
    def _logger(self):
        if hasattr(self, '_memoize_logger'):
            return self._memoize_logger

        self._memoize_logger = logging.getLogger('ggacha')
        return self._memoize_logger

    def _write_log(self, f, message, *args, **kwargs):
        try:
            f(u'[%s] %s: ' + message,
              threading.currentThread().getName(),
              self.__class__.__name__,
              *args, **kwargs)
        except:
            self.write_log_except()

    def write_log_except(self):
        stack_trace = ''.join(traceback.format_exception(*sys.exc_info()))
        self._logger.error(u'[%s] %s:\n%s',
                           threading.currentThread().getName(),
                           self.__class__.__name__,
                           stack_trace)

    def write_log_debug(self, message, *args, **kwargs):
        self._write_log(self._logger.debug, message, *args, **kwargs)

    def write_log_info(self, message, *args, **kwargs):
        self._write_log(self._logger.info, message, *args, **kwargs)

    def write_log_warn(self, message, *args, **kwargs):
        self._write_log(self._logger.warn, message, *args, **kwargs)

    def write_log_error(self, message, *args, **kwargs):
        self._write_log(self._logger.error, message, *args, **kwargs)
