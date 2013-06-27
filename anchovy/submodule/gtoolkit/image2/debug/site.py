# -*- coding: utf-8 -*-
from PIL import Image
from django.conf import settings
from django.http import HttpResponse
from django.views.generic import View
from ..image import FORMAT
from .image import DUMMIES


class DebugImageView(View):
    def get(self, request, *args, **kwargs):
        image_format = kwargs.get('format', 'PNG').upper()
        width = int(kwargs.get('width', 300))
        height = int(kwargs.get('height', 400))

        response = HttpResponse(
            content_type='image/{}'.format(image_format))
        img = Image.new('RGBA', (width, height))
        img.save(response, image_format)
        return response


class DebugImageIDView(View):
    def get(self, request, *args, **kwargs):
        dummy_image = DUMMIES[kwargs['dummy_key']]
        response = HttpResponse(
            content_type='image/{}'.format(dummy_image.format.ext))
        dummy_image.pil_image.save(response, FORMAT.get(dummy_image.format.ext,
                                                        'PNG'), quality=95)
        return response


class DebugImageSite(object):
    def __init__(self, name='debug_image', app_name='debug_image'):
        self.name = name
        self.app_name = app_name

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.name

    def get_urls(self):
        from django.conf.urls import patterns, url

        if not settings.DEBUG:
            return patterns('')

        return patterns(
            '',
            url(r'^$', DebugImageView.as_view(),
                name='gtoolkit_debug_image_render'),
            url(r'^(?P<format>.+)/(?P<width>.+)/(?P<height>.+)/$', DebugImageView.as_view(),
                name='gtoolkit_debug_image_render'),
            url(r'^(?P<dummy_key>[a-z0-9-]+)/$', DebugImageIDView.as_view(),
                name='gtoolkit_debug_image_render'),
        )

site = DebugImageSite()
