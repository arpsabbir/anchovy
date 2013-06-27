# -*- coding: utf-8 -*-
import logging
import sys
import threading
import traceback

class Logger(object):
    def __init__(self, name):
        self._logger = logging.getLogger(name)

    def _write(self, f, message, *args, **kwargs):
        if not kwargs.get('verbose', True): # verbose=True で出力
            return                          # 未指定で True

        if kwargs.has_key('verbose'): # ログに verbose フラグは表示しない
            del kwargs['verbose']

        try:
            f(u'[%s]: ' + message,
              threading.currentThread().getName(),
              *args, **kwargs)
        except:
            self.except_error()

    def except_error(self):
        stack_trace = ''.join(traceback.format_exception(*sys.exc_info()))
        self._logger.error(u'[%s]:\n%s',
                           threading.currentThread().getName(),
                           stack_trace)

    def debug(self, message, *args, **kwargs):
        self._write(self._logger.debug, message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        self._write(self._logger.info, message, *args, **kwargs)

    def warn(self, message, *args, **kwargs):
        self._write(self._logger.warn, message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self._write(self._logger.error, message, *args, **kwargs)
