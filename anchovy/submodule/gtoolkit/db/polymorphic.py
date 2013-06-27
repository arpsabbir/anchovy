# -*- coding: utf-8 -*-
"""
単一テーブル継承(STI)を実現する.

モデルの準備
------------

.. code-block:: python

    from abc import abstractmethod
    from django.db import models

    from gtoolkit.db.polymorphic import PolymorphicModel

    class Engineer(PolymorphicModel):
        python = IntegerField(default=0)
        ruby = IntegerField(default=0)
        
        @abstractmethod
        def vote(self):
            pass

    class Ikuta(Engineer):
        class Meta:
            proxy = True

        def vote(self):
            self.python += 1

    class Imamura(Engineer):
        class Meta:
            proxy = True

        def vote(self):
            self.ruby += 1


使用方法
--------

>>> ikuta = Ikuta()
>>> ikuta.python # 0
>>> ikuta.ruby # 0
>>> ikuta.vote()
>>> ikuta.python # 1
>>> ikuta.ruby # 0
>>> ikuta.save()

>>> imamura = Imamura()
>>> imamura.python # 0
>>> imamura.ruby # 0
>>> imamura.vote()
>>> imamura.python # 0
>>> imamura.ruby # 1
>>> imamura.save()

>>> Engineer.objects.all() # [<Ikuta: Ikuta object>, <Imamura: Imamura object>]
>>> Ikuta.objects.all() # [<Ikuta: Ikuta object>]
>>> Imamura.objects.all() # [<Imamura: Imamura object>]


安全な使い方
------------

モジュール名とクラス名を DB に保存していると,
SQL Injection 攻撃を受けることで, 任意のクラスをロードされる可能性がある.

次の様に BaseClass.classes にマッピング表を登録すると
DB には, クラスと紐づいたキー値のみが入るため, SQL Injection 攻撃を受けても
任意のクラスがロードされない.

.. code-block:: python

    class Engineer(PolymorphicModel):
        pass

    class Ikuta(Engineer):
        class Meta:
            proxy = True

    class Imamura(Engineer):
        class Meta:
            proxy = True

    Engineer.classes = {
        Ikuta: 'ikt',
        Imamura: 'imr',
    }
"""
from django.db import models


class PolymorphicScopeMixin(object):
    def by_cls(self):
        if not self.model.classes:
            return self.filter(mod=self.model.__module__,
                               cls=self.model.__name__,)

        return self.filter(mod='mapping', cls=self.model.classes[self.model])


class PolymorphicQuerySet(models.query.QuerySet, PolymorphicScopeMixin):    
    pass


class PolymorphicManager(models.Manager, PolymorphicScopeMixin):
    def get_query_set(self):
        qs = PolymorphicQuerySet(self.model)
        return qs.by_cls() if self.model._meta.proxy else qs


class PolymorphicModel(models.Model):
    class ClassesKeyError(Exception):
        pass

    class SaveBaseError(Exception):
        pass

    class Meta:
        abstract = True

    objects = PolymorphicManager()

    mod = models.CharField(max_length=255)
    cls = models.CharField(max_length=255)

    classes = None

    @staticmethod # Django Model の癖で, static 宣言をあえて行う必要がある
    def __new__(cls, *args, **kwargs):
        arg_mod, arg_cls = cls._parse_args(*args, **kwargs)

        if arg_cls is None:
            return super(PolymorphicModel, cls).__new__(cls, *args, **kwargs)

        cls = cls._get_class(arg_mod, arg_cls)
        return super(PolymorphicModel, cls).__new__(cls, *args, **kwargs)

    @classmethod
    def _parse_args(cls, *args, **kwargs):
        arg_mod = kwargs.get('mod', None)
        arg_cls = kwargs.get('cls', None)

        for field, arg in zip(cls._meta.fields, args):
            if arg_mod is not None and arg_cls is not None:
                break

            if field.name == 'mod':
                arg_mod = arg
            elif field.name == 'cls':
                arg_cls = arg

        if arg_cls is not None:
            assert arg_mod is not None # 念のため, c と m がセットである事を保証
            arg_mod = str(arg_mod)
            arg_cls = str(arg_cls)

        return arg_mod, arg_cls

    # 何度も __import__ が呼ばれないよう, メモ化しておく
    _class_memo = {}

    @classmethod
    def _get_class(cls, arg_mod, arg_cls):
        if cls.classes: # マッピング表が存在する
            for cls, key in cls.classes.iteritems():
                if key == arg_cls:
                    return cls
            raise cls.ClassesKeyError(u'{} is not found'.format(arg_cls))

        if PolymorphicModel._class_memo.has_key((arg_mod, arg_cls)):
            return PolymorphicModel._class_memo[(arg_mod, arg_cls)]

        loaded_cls = getattr(__import__(arg_mod, globals(), locals(), [arg_cls]),
                             arg_cls)
        PolymorphicModel._class_memo[(arg_mod, arg_cls)] = loaded_cls
        return loaded_cls
   
    def save(self, *args, **kwargs):
        if not self._meta.proxy:
            raise self.SaveBaseError(u'Model is not proxy.')

        self._set_cls()
        return super(PolymorphicModel, self).save(*args, **kwargs)

    def _set_cls(self):
        if self.cls:
            return

        if not self.classes:
            self.mod = self.__class__.__module__
            self.cls = self.__class__.__name__
            return

        self.mod = 'mapping'
        self.cls = self.classes[self.__class__]
