#coding: utf-8

from kome.core.actionlog import ActionLog, ActionRecord
from kome.middleware.log_context import LogContext
from kome.middleware._util import ignore_exception_if_no_debug,ScopeExit
import kome.middleware._log as l

class ActionLogger(object):
    def __init__(self, sender, userid, devicename, parent = None, parentid = None):
        assert parent is     None and parentid is     None or\
               parent is not None and parentid is not None

        self._actlog = ActionLog(sender, userid, devicename)
        if parent is None:
            self._record = None
        else:
            self._record = ActionRecord(parentid, parent, None, self._actlog)

    @property
    def uid(self):
        return self._actlog.uid

    @property
    def device(self):
        return self._actlog.device

    def __enter__(self):
        self.begin()

    def begin(self):
        l.set_log(LogContext(l.enter_context, l.exit_context))

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.flush()
        return False

    def flush(self):
        ignore_exception_if_no_debug(self._flush)

    def _flush(self):
        lc = l.log()
        with ScopeExit(lambda: lc.clear()):
            if self._record is None:
                lc.flush(self._actlog)
            else:
                lc.flush_with_parent(self._record)
