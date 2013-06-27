#coding: utf-8

from kome.middleware import _settings

class ScopeExit(object):
    def __init__(self, f): self._f = f
    def __enter__(self): pass
    def __exit__(self, exc_type, exc_value, traceback):
        self._f()
        return False

def ignore_exception_if_no_debug(f, raise_value = None):
    if _settings.is_debug():
        return f()
    else:
        try:
            return f()
        except Exception:
            import logging
            import traceback
            import sys

            info = sys.exc_info()
            type = info[0]
            value = info[1]
            tb = traceback.format_exc(info[2])

            logger = logging.getLogger(__name__)
            logger.error('%s, %s, %s', type, value, tb)

            return raise_value
