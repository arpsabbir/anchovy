# -*- coding:utf-8 -*-
from django.conf.urls import patterns, url
from apps.website.v_root.views.top import RootTopView

urlpatterns = patterns(
    '',
    url(r'^$', RootTopView.as_view(), name='root_index'),
)
