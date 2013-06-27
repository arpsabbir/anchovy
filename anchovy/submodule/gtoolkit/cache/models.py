# -*- coding: utf-8 -*-
from django.db import models

from gtoolkit.cache.method_cache import (method_cache, delete_method_cache)

class CachedMasterModel(models.Model):
    """
    キャッシュ機能を持つ Model
    更新が少ないマスターデータの管理に使用する
    """
    class Meta:
        abstract = True


    def save(self, *args, **kwargs):
        super(CachedMasterModel, self).save(*args, **kwargs)
        self.delete_cache()

    def delete(self, *args, **kwargs):
        self.delete_cache()
        super(CachedMasterModel, self).delete(*args, **kwargs)

    def delete_cache(self):
        """
        save と delete から呼ばれるので, CachedMasterModel を継承した Model で
        method_cache でデコレートしたクラスメソッドを作ったならば,
        このメソッドを上書きして delete_method_cache を呼ぶ事.
        その際, super で CachedMasterModel の delete_cache も忘れずに呼ぶ事.
        """
        delete_method_cache(self, self.get, args=(self.pk,))
        delete_method_cache(self, self.get_all)

    @classmethod
    @method_cache
    def get(cls, pk):
        return cls.objects.get(pk=pk)

    @classmethod
    @method_cache
    def get_all(cls):
        return list(cls.objects.all())
