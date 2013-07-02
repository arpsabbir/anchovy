# -*- coding: utf-8 -*-
from gtoolkit.cache.models import CachedMasterModel
from django.db import models
from gtoolkit.db import EnableFlagMixin, NameFieldMixin


class ResRepository(CachedMasterModel, EnableFlagMixin, NameFieldMixin):
    """
    書き込み実態データを保存するテーブル
    """
    sure_id = models.IntegerField(default=0)
    resu_id = models.IntegerField(default=0)
    resu_number = models.IntegerField(default=0)
    message = models.TextField()

    class Meta(object):
        app_label = 'res'
        unique_together = ('resu_id', 'resu_number')