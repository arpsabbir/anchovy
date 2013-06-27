#coding: utf-8

from kome.middleware.null_log_context import NullLogContext

try:
    from threading import local
except ImportError:
    try:
        from django.utils._threading_local import local
    except ImportError:
        from dummy_threading import local

def enter_context(old, new):
    _thread_locals.log_context = new
def exit_context(old, new):
    _thread_locals.log_context = old

_thread_locals = local()
_null_context = NullLogContext()

def log():
    try:
        return _thread_locals.log_context
    except:
        return _null_context

def set_log(lc):
    _thread_locals.log_context = lc
