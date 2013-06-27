# -*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url

# root
urlpatterns = patterns(
    '',
    url('', include('apps.website.v_root.urls')),
)