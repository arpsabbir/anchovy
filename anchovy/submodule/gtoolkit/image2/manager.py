# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.utils.functional import cached_property
try:
    from django.utils.six import string_types
except ImportError:
    # Django 1.4以下対応
    string_types = basestring

from .exceptions import AliasTargetNotFoundError


class ImageManager(object):
    """
    複数画像を管理するクラス

    ラベル名から単体画像用のクラスを返す
    """
    @cached_property
    def labels(self):
        return self.label_map.keys()

    @cached_property
    def images(self):
        return {name: self.image_map[name](
            self.path_format,
            self.base_params,
            instance=self.instance,
        ) for name in self.image_map.keys()}

    def __init__(self, base_params, path_format, image_map, label_map,
                 device_name=None, label_prefix=None, instance=None):
        self.base_params = base_params
        self.path_format = path_format

        self.image_map = image_map
        self.label_map = label_map

        self.device_name = device_name
        self.label_prefix = label_prefix if label_prefix else ''
        self.instance = instance

    def __getattr__(self, item):
        return self._get(item)

    def __getitem__(self, item):
        return getattr(self, item)

    def _get(self, name):

        if self.is_label_dir(name):
            # ラベルに下の階層がある
            return ImageManager(
                base_params=self.base_params,
                path_format=self.path_format,
                image_map=self.image_map,
                label_map=self.label_map[name],
                label_prefix=self.get_full_label(name))

        if self.is_label_image(name):
            # 画像が確定した
            return self._get_image(self.label_map[name])

        return None

    def _get_image(self, full_label):
        if full_label not in self.image_map:
            return None

        return self.image_map[full_label](
            self.path_format,
            self.base_params,
            instance=self.instance,
        )

    def is_label_dir(self, name):
        return name in self.label_map and isinstance(self.label_map[name], dict)

    def is_label_image(self, name):
        return name in self.label_map and isinstance(self.label_map[name],
                                                     string_types)

    def get_full_label(self, name):
        return '{DEVICE}.{PREFIX}{NAME}'.format(
            DEVICE=self.device_name,
            PREFIX=self.label_prefix + '.' if self.label_prefix else '',
            NAME=name)

    def validate(self, name, dummy_off=False):
        image = self._get(name)
        if not image:
            raise AliasTargetNotFoundError(
                '{} image cannot found. alias from {}'.format(
                    self.label_map[name], name))

        if dummy_off:
            image.dummy_image = None

        return image.is_valid()
