# -*- coding: utf-8 -*-
from gtoolkit.cache.models import CachedMasterModel
from django.db import models
from gtoolkit.db import EnableFlagMixin, NameFieldMixin


class Ita(CachedMasterModel, EnableFlagMixin, NameFieldMixin):
    group = models.IntegerField()
    url = models.CharField(max_length=255)

    # 格納されているスレ数
    sure_number = models.IntegerField(default=0)

    # Faild_count DL失敗したときの連続失敗数をカウントする

    class Meta(object):
        app_label = 'ita'
        unique_together = ('url', )