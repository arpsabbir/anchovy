# -*- coding: utf-8 -*-
from django.conf import settings
from .views import get_template_article_keys


class MockSite(object):
    def __init__(self, name='mock', app_name='mock'):
        self.name = name
        self.app_name = app_name

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

    def get_urls(self):
        from django.conf.urls import patterns, url

        if not settings.DEBUG:
            return patterns('')

        from .views import MockView
        return patterns(
            '',
            url(r'^(?P<path>.+)$', MockView.as_view(), name='mock_render'),
        )

site = MockSite()
