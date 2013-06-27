# -*- coding:utf-8 -*-
import os
import re
from PIL import Image as PIL_Image
from django.utils.functional import cached_property
from ..image import (ImageFormat as OriginalImageFormat)
from .device import IMAGE_BASE_URL
from .exceptions import (InvalidImageSizeError, InvalidImageProgressiveError,
                         ImageDoesNotExist, InvalidImageFormatError)


FORMAT = {
    'jpg': 'jpeg',
    'png': 'png',
    'gif': 'gif',
}


class Image(object):
    def __init__(self, base_path, url_base_path, path, image_format,
                 instance=None, require_validate=None):
        self.base_path = base_path
        self.url_base_path = url_base_path
        self.path = path
        self.image_format = image_format
        self.instance = instance
        self.require_validate = require_validate

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.path

    @property
    def url(self):
        return '{}/{}'.format(self.url_base_path, self.path)

    @property
    def absolute_path(self):
        """
        画像への絶対パスを返す
        """
        return os.path.join(os.path.join(self.base_path, self.path))

    @property
    def reactive_path(self):
        """
        画像へのIMAGE_URLからの相対パスを返す
        """
        return re.sub('^{}'.format(IMAGE_BASE_URL), '', self.url)

    @cached_property
    def media(self):
        """
        画像のバイナリデータを返す
        """
        return open(self.absolute_path).read()

    @property
    def format(self):
        return self.image_format

    @property
    def is_exists(self):
        """
        ファイルの存在確認
        """
        return os.path.exists(self.absolute_path)

    @cached_property
    def pil_image(self):
        """
        画像をPILでロードして返す
        """
        image = PIL_Image.open(self.absolute_path)
        image.load()
        return image

    def is_valid(self):
        """
        ファイルが正しいかどうかを返す
        """
        if callable(self.require_validate):
            # バリデーションするかの評価関数が指定されている

            if not self.require_validate(self.instance):
                # 偽を返したのでチェックしないでパス
                return True

        elif self.require_validate is False:
            # 明示的にバリデーションしない事を指定
            return True

        if not self.is_exists:
            # 存在しない
            raise ImageDoesNotExist(
                "{}".format(
                    self.reactive_path
                )
            )

        # 画像サイズチェック
        if not self._check_image_size():
            raise InvalidImageSizeError(
                "O {}:{} -> X {}:{} [{}]".format(
                    self.image_format.width,
                    self.image_format.height,
                    self.pil_image.size[0],
                    self.pil_image.size[1],
                    self.reactive_path
                )
            )

        # 画像フォーマットチェック
        if not self._check_image_format():
            raise InvalidImageFormatError(
                "O {} -> X {} [{}]".format(
                    self.image_format.ext,
                    self.pil_image.tile[0][0],
                    self.reactive_path
                )
            )

        # プログレッシブ画像チェック
        if not self._check_progressive():
            raise InvalidImageProgressiveError(
                "{}".format(
                    self.reactive_path
                )
            )

        # OK
        return True

    def _check_progressive(self):
        """
        JPEGのプログレッシブ画像かチェックする
        """
        return not (self.image_format.check_progressive
                    and 'progression' in self.pil_image.info.has_key
                    and self.pil_image.info['progression'] == 1)

    def _check_image_size(self):
        """
        画像のサイズチェック
        """
        return (self.pil_image.size[0] == self.image_format.width) \
            and (self.pil_image.size[1] == self.image_format.height)

    def _check_image_format(self):
        """
        画像のフォーマットチェック
        """
        return self.pil_image.format.lower() == FORMAT.get(self.image_format.ext).lower()


class ImageFormat(OriginalImageFormat):
    def __init__(self, ext, width, height, view_width=None, view_height=None):
        super(ImageFormat, self).__init__(ext, width, height,
                                          view_width=view_width,
                                          view_height=view_height)
