# coding: utf-8

class NullLogContext(object):
    def __init__(self):
        self._derivedlog = None

    def __getattr__(self, actname):
        context = self
        class Proxy(object):
            def __init__(self, **kwargs):
                pass

            def __enter__(self):
                return context

            def __exit__(self, exec_type, exec_val, exec_tb):
                return False

        return Proxy

    def log(self, actname, **kwargs):
        return self.__getattr__('log')(actname=actname, **kwargs)

    def set(self, **kwargs):
        pass

    class NullDerivedLog(object):
        def __getattr__(self, name):
            def proxy(*args, **kwargs):
                pass
            return proxy

    @property
    def derivedlog(self):
        if self._derivedlog is None:
            self._derivedlog = self.NullDerivedLog()
        return self._derivedlog

    def clear(self):
        pass

    def flush(self, actlog):
        pass
