# -*- coding: utf-8 -*-
from gtoolkit.cache.models import CachedMasterModel
from django.db import models
from gtoolkit.db import EnableFlagMixin, NameFieldMixin


class Res(CachedMasterModel, EnableFlagMixin):
    sure_id = models.IntegerField(default=0)
    good = models.IntegerField(default=0)
    bad = models.IntegerField(default=0)

    class Meta(object):
        app_label = 'res'
        # unique_together = ('url', )