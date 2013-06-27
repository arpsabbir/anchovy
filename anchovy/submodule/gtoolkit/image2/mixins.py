# -*- coding:utf-8 -*-
import os
from collections import defaultdict
from django.conf import settings
from django.utils.functional import cached_property
from .device import (DEVICE_NAME_MAP, IMAGE_ROOT_PATH, IMAGE_BASE_URL,
                     get_device_image_dir_name)
from gtoolkit.image2.debug import DebugImage
from .image import ImageFormat, Image
from .manager import ImageManager


def image(name, ext, width, height,
          extend_base_path=None, extend_dir_params=None,
          require_validate=None, path_format=None):
    """
    Image生成用関数を作成する
    実画像用

    :param name: 画像名
    :param ext: 拡張子
    :param width: 横px
    :param height: 縦px
    :param extend_base_path: ベースパスに追加するパス名
    :type extend_base_path: list
    :param extend_dir_params: パス生成時に使う情報
    :type extend_dir_params: dict
    :param require_validate: validationを行うかの指定
    :type require_validate: callable or bool or None
    :param path_format: 独自のimage_path_formatを指定できる
    :type path_format: str or unicode
    """
    def _image_factory(device_name):
        """
        :return:
        """
        name_entities = [device_name]
        base_path = os.path.join(IMAGE_ROOT_PATH, device_name)

        if extend_base_path:
            name_entities.extend(extend_base_path)
            base_path = os.path.join(base_path, *extend_base_path)

        image_name = '.'.join(name_entities + [name])

        url_base_path = IMAGE_BASE_URL + device_name

        def _image(instance_path_format, base_params, instance=None):
            """
            最終的なImageのインスタンスを作る関数　

            :type instance_path_format: str or unicode
            :param base_params:
            :type base_params: dict
            """
            params = {
                'filename': name,
                'label': name,
                'ext': ext,
            }
            params.update(base_params)

            if extend_dir_params:
                params.update(extend_dir_params)

            if path_format:
                path = path_format.format(**params)
            else:
                path = instance_path_format.format(**params)

            image_class = DebugImage if settings.DEBUG else Image

            return image_class(
                base_path=base_path,
                url_base_path=url_base_path,
                path=path,
                image_format=ImageFormat(ext=ext, width=width, height=height),
                instance=instance,
                require_validate=require_validate,
            )

        return image_name, _image

    return _image_factory


def label(name, alias=None):
    """
    実画像への参照

    :param name: ラベル名.外側からアクセスする時の名前
    :param alias: 画像名
    :return: (ラベル名, 画像名)
    """
    image_name = alias
    if not alias.startswith(('featurephone', 'smartphone')):
        image_name = '_default.' + alias
    return name, image_name


def image_manager(*args, **kwargs):
    """
    ImageManagerを生成する関数を生成する
    """
    images = {}
    for image_factory_func in args:
        image_name, image_func = image_factory_func('_default')
        images[image_name] = image_func

    label_map = defaultdict(dict)
    for device_name, labels in kwargs.items():
        if device_name not in DEVICE_NAME_MAP:
            continue

        for label_name, image_name in labels:
            label_map[device_name][label_name] = image_name

    def _manager(instance, device_name=None, mobilejp_device=None, **kwargs):
        base_params = instance.get_image_base_params()
        path_format = instance.get_image_path_format()
        current_device_name = get_device_image_dir_name(
            name=device_name, mobilejp_device=mobilejp_device)

        return ImageManager(base_params, path_format,
                            images, label_map[current_device_name],
                            device_name=get_device_image_dir_name(),
                            instance=instance, **kwargs)

    return _manager


class ImageMixin(object):
    """
    画像用のプロパティを追加するMixinクラス

    image_path_format
      画像のパス構造を設定して下さい。
      /card/カードID/サイズ名.拡張子のような構造の場合は
      {base_name}/{id}/{label}.{ext}のように設定します。

    _images
      画像のファイルフォーマット、拡張子、サイズなどを種類ごとに渡します。
      以下のような構造にします。

    _images = images(
        image('FP.large', ImageFormat(ext='jpg', width=640, height=960)),
        image('sp.large', ImageFormat(ext='png', width=640, height=960)),
        image('medium', ImageFormat(ext='png', width=640, height=960)),
        image('medium_fp', ImageFormat(ext='jpg', width=640, height=960)),
        image('small', ImageFormat(ext='png', width=640, height=960)),
        image('mini', ImageFormat(ext='gif', width=640, height=960)),

        featurephone=(
            label('large', alias='FP.large'),
            label('medium', alias='medium'),
            label('small', alias='small'),
        ),
        smartphone=(
            label('large', alias='large'),
            label('medium', alias='medium'),
            label('small', alias='small'),
        ),
    )
    """
    image_path_format = os.path.join('{base_name}', '{id}', '{filename}.{ext}')
    _image_manager = image_manager(
        image('large', ext='png', width=640, height=960),
        image('large_fp', ext='jpg', width=640, height=960),
        image('medium', ext='png', width=640, height=960),
        image('medium_fp', ext='jpg', width=640, height=960),
        image('small', ext='png', width=640, height=960),
        image('mini', ext='gif', width=640, height=960),

        featurephone=(
            label('large', alias='large'),
            label('medium', alias='medium'),
            label('small', alias='small'),
        ),
        smartphone=(
            label('large', alias='large_fp'),
            label('medium', alias='medium'),
            label('small', alias='small'),
        ),
    )

    @cached_property
    def image(self):
        return self._get_image_manager()

    def _get_image_manager(self, **kwargs):
        return self._image_manager(**kwargs)

    def get_base_name(self):
        try:
            app_label = self._meta.app_label
        except AttributeError:
            paths = self.__module__.split('.')
            app_label = paths[-2]
            if app_label == 'models':
                app_label = paths[-3]

        return app_label + '_' + self.get_base_class_name()

    def get_base_class_name(self):
        return self.__class__.__name__.lower()

    def get_image_path_format(self):
        return self.image_path_format

    def get_image_base_params(self):
        return {
            'base_name': self.get_base_name(),
            'id': self.pk,
        }
