# coding: utf-8

import inspect
from kome.core.actionlog import ActionLog
from kome.core.derivedlog import DerivedLog
from kome.middleware import _settings
from kome.middleware.method_pool import MethodPool
import uuid

def _check_callable(cls, method, *args, **kwargs):
    if hasattr(inspect, 'getcallargs'):
        # for Python 2.7 or later.
        inspect.getcallargs(getattr(cls, method), cls, *args, **kwargs)
    else:
        # for Python 2.6 or earlier.
        if not hasattr(cls, method):
            raise AttributeError, 'This class has not attr: ' + method

class LogContext(object):
    def __init__(self, enter, exit, actname = None, kwargs = None):
        self._actname = actname
        self._kwargs = kwargs or {}
        self._derivedlog = None
        self._childs = []
        self._enter = enter
        self._exit = exit
        if self._actname is not None:
            self._id = str(uuid.uuid4())
        else:
            self._id = None

    def __getattr__(self, actname):
        if not hasattr(ActionLog, actname):
            raise AttributeError, 'ActionLog has not attr: ' + actname

        context = self
        class Proxy(object):
            def __init__(self, **kwargs):
                self._kwargs = kwargs
                self._log = None

            def __enter__(self):
                log = LogContext(context._enter,
                                 context._exit,
                                 actname,
                                 self._kwargs)

                context._enter(context, log)
                self._log = log

                return log

            def __exit__(self, exec_type, exec_val, exec_tb):
                log = self._log
                if exec_type is None:
                    # check callable
                    if _settings.is_debug():
                        actname = log._actname
                        kwargs = log._kwargs
                        _check_callable(ActionLog, actname, **kwargs)

                    context._childs.append(log)

                context._exit(context, log)

                return False

        return Proxy

    @property
    def id(self):
        if 'id' in self._kwargs:
            return self._kwargs['id']
        return self._id

    @property
    def actname(self):
        if 'actname' in self._kwargs:
            return self._kwargs['actname']
        return self._actname

    def log(self, actname, **kwargs):
        return self.__getattr__('log')(actname=actname, **kwargs)

    def set(self, **kwargs):
        self._kwargs.update(kwargs)

    @property
    def derivedlog(self):
        if self._derivedlog is None:
            self._derivedlog = MethodPool(DerivedLog)
        return self._derivedlog

    def clear(self):
        self._child = []
        self._derivedlog = None

    def _merge_id(self, dic):
        m = dict(dic)
        if 'id' not in m:
            m['id'] = self.id
        return m

    def flush(self, actlog):
        if self._actname is None:
            if self._derivedlog is not None:
                self._derivedlog.call_methods(DerivedLog(actlog, None))
            for child in self._childs:
                child.flush(actlog)
        else:
            kwargs = self._merge_id(self._kwargs)
            record = getattr(actlog, self._actname)(**kwargs)
            if self._derivedlog is not None:
                self._derivedlog.call_methods(record.get_derivedlog())
            for child in self._childs:
                child.flush(record.get_actlog())
        self.clear()

    def flush_with_parent(self, record):
        actlog = record.get_actlog()
        if self._actname is None:
            if self._derivedlog is not None:
                self._derivedlog.call_methods(DerivedLog(actlog, record))
            for child in self._childs:
                child.flush(actlog)
        else:
            self.flush(actlog)
        self.clear()
