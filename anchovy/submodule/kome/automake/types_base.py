# coding: utf-8

def _isinstance(instance, cls):
    if hasattr(cls, '_instancecheck'):
        return cls._instancecheck(instance)
    else:
        return isinstance(instance, cls)

class NumberTypes:
    _classes = []
    @classmethod
    def _instancecheck(cls, instance):
        return any([_isinstance(instance, c) for c in cls._classes])
    @classmethod
    def register(cls, subclass):
        cls._classes.append(subclass)
NumberTypes.register(int)
NumberTypes.register(long)

class StringTypes:
    _classes = []
    @classmethod
    def _instancecheck(cls, instance):
        return any([_isinstance(instance, c) for c in cls._classes])
    @classmethod
    def register(cls, subclass):
        cls._classes.append(subclass)
StringTypes.register(str)
StringTypes.register(unicode)

#############################
# 以下自動生成で出力した実装
#############################
