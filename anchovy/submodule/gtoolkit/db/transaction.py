# -*- coding: utf-8 -*-
"""
django.db.transaction.savepoint を with に対応.

使い方は次の通り.

.. code-block:: python

    from gtoolkit.db.transaction import savepoint

    with savepoint():
       obj.ham = 'egg'
       obj.save()


with ブロックの終了時に, with ブロック内の Django Model の更新が commit される.
with ブロック内で例外が発生すると rollback される.

トランザクションの失敗を捕捉する例は次の通り.

.. code-block:: python

    from django.db import IntegrityError
    from gtoolkit.db.transaction import savepoint

    try:
        with savepoint():
           obj.ham = 'egg'
           obj.save()
    except IntegrityError, e:
        # トランザクションの例外
        pass
    except SpamError, e:
        # トランザクション以外の例外
        pass


垂直分割で使用する場合, savepoint の第一引数 using に DB 名を指定する事.

.. code-block:: python
    with savepoint(using='guild'):
       obj.ham = 'egg'
       obj.save()
"""
from functools import wraps
from django.db import transaction

class _Savepoint(object):
    def __init__(self, using=None):
        self._using = using

    def __enter__(self):
        self._sid = transaction.savepoint(using=self._using)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            transaction.savepoint_commit(self._sid, using=self._using)
            return True
        else:
            transaction.savepoint_rollback(self._sid, using=self._using)
            return False

    def __call__(self, func):
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)
        return inner


def savepoint(using=None):
    return _Savepoint(using=using)
