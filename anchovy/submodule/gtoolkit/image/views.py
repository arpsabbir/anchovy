# -*- coding:utf-8 -*-
"""
Image View Base
"""

import StringIO
from collections import OrderedDict

from django import http
try:
    from django.views.generic.base import View
except ImportError:
    View = object  # テスト用

from PIL import Image, ImageDraw


class ImageFileDoesNotExistsError(Exception):
    pass


class PILImageView(View):
    """
    PIL画像をレスポンスするビュー基底クラス
    """
    MIMETYPE = 'image/jpeg'
    IMAGE_TYPE = 'jpeg'
    CACHE_AGE = 3600

    def get_pil_image(self, request, *args, **kwargs):
        """
        PILイメージオブジェクトを返すテンプレートメソッド
        :return: PIL image object
        """
        raise NotImplementedError('{}:{}'.format(
            self.__class__.__name__, 'get_image'))

    def convert_image_to_binary(self, image):
        sio = StringIO.StringIO()
        image.save(sio, self.IMAGE_TYPE)
        sio.seek(0)
        return sio.read()

    def get(self, request, *args, **kwargs):
        image = self.get_pil_image(request, *args, **kwargs)
        if image is None:
            raise Exception(
                '{}.get_pil_image() must be returned image object.'.format(
                self.__class__.__name__))
        image_binary = self.convert_image_to_binary(image)
        response = http.HttpResponse(mimetype=self.MIMETYPE)
        response.write(image_binary)
        if self.CACHE_AGE:
            response['Cache-Control'] = 'max-age={}'.format(self.CACHE_AGE)
        return response


class PILImageLayerMixin(object):
    """
    self._image に対して編集を行うクラス
    PILImageViewにMixinして使うことを想定
    """

    def get_image(self):
        return self._image

    def set_image(self, image):
        self._image = image

    def initialize_image(self, *args, **kwargs):
        """
        空画像を作成。PIL.Image の、引数をそのまま受け取る
        :param 0: mode
        :param 1: size
        例: initialize_image('RGBA', (100,100,))
        """
        self._image = Image.new(*args, **kwargs)

    def layer_image(self, layer_image, failed_image_path=None,
                    center=None, origin=None, size=None,
                    ellipse_center=None, ellipse_radius=None):
        """
        画像を合成、self._image を直接変更する
        :param layer_image: 画像のパス, PIL Image, gtoolkit.image2.Image どれか
        :param center: (tuple) 画像合成の中心
        :param origin: (tuple) 画像合成の原点 centerが指定されていれば無視される
        :param ellipse_center: 円形切り抜きの中心点(layer_image に対して)
        :param ellipse_radius: 円形切り抜きの半径(px)
        """
        if isinstance(layer_image, basestring):
            # 画像パスだったらそれを読み込み
            layer_image = self._get_image_or_failed_image(
                layer_image, failed_image_path)
        else:
            if hasattr(layer_image, 'pil_image'):
                # gtoolkit2 の Image だった
                layer_image = layer_image.pil_image
        if ellipse_center or ellipse_radius:
            layer_image = self.mask_ellipse(
                layer_image, radius=ellipse_radius,
                center=ellipse_center)
        self._simple_layer_image(layer_image, center=center, origin=origin, size=size)

    @classmethod
    def _get_image_or_failed_image(cls, image_path, failed_image_path=None):
        """
        :param image_path: 画像パス
        :param failed_image_path: 画像が無いときの画像パス
        :return: PIL 画像オブジェクト
        """
        try:
            layer_image = Image.open(image_path)
        except IOError:
            if failed_image_path is not None:
                layer_image = Image.open(failed_image_path)
                layer_image.load()
                return layer_image
            raise ImageFileDoesNotExistsError(image_path)
        else:
            layer_image.load()
            return layer_image

    def _simple_layer_image(self, layer_image, center=None, origin=None, size=None):
        """
        :param center: (tuple) 画像合成の中心
        :param origin: (tuple) 画像合成の原点 centerが指定されていれば無視される
        """
        X, Y = 0, 1
        if size is not None:
            layer_image = layer_image.copy()
            layer_image.thumbnail(size, Image.ANTIALIAS)
        mask = None
        if layer_image.mode in ['RGBA', ]:
            mask = layer_image.split()[3]
        if center:
            layer_center = map(lambda x: x / 2, layer_image.size)
            offset = center[X] - layer_center[X], center[Y] - layer_center[Y]
            self._image.paste(layer_image, offset, mask=mask)
        elif origin:
            offset = origin[X], origin[Y]
            self._image.paste(layer_image, offset, mask=mask)
        else:
            self._image.paste(layer_image, layer_image.getbbox(), mask=mask)

    @classmethod
    def mask_ellipse(cls, image, radius=None, center=None):
        """
        imageを円形に切り抜くアルファを作成し、くっつける
        :param center: 中心点 タプル(x, y)
        :param radius: 半径
        """
        image = image.convert('RGBA')
        mask = Image.new("L", image.size, 1)
        draw = ImageDraw.Draw(mask)

        X, Y = 0, 1

        if center is None:
            center = map(lambda x: x / 2, image.size)
        if radius is None:
            radius = map(lambda x: x / 2, image.size)
        elif not isinstance(radius, (list, tuple,)):
            radius = (radius, radius,)

        start = [center[d] - radius[d] for d in (X, Y)]
        end = [center[d] + radius[d] for d in (X, Y)]

        draw.ellipse((start[X], start[Y], end[X], end[Y]), fill="#ffffff")
        image.putalpha(mask)
        return image

    def resize(self, size):
        """
        画像をリサイズ。
        :param size: タプル(width, height)
        """
        self._image = self._image.resize(size, Image.ANTIALIAS)


class ImageLayerTag(object):
    """
    divタグで画像を重ねて、最後にdivタグでかこって出力するクラス
    SP用のテンプレートタグで、マイページ画像を表示する時に使う
    """

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.htmls = []
        self.z_index = 0

    def layer_image(self, layer_image_url, size=None):
        style = OrderedDict()
        style['position'] = 'absolute'
        style['top'] = '0'
        style['left'] = '0'
        if size:
            style['width'] = self.to_pixel(size[0])
            style['height'] = self.to_pixel(size[1])
        style['z-index'] = str(self.z_index)
        html = '<img src="{}" {} />'.format(layer_image_url, self.style_attr(style))
        self.htmls.append(html)
        self.z_index += 1

    def layer_image_ellipse(self, layer_image_url, center, ellipse_radius):
        """
        :param center: タプル(X,Y) 配置中心位置
        :param ellipse_radius: マスク半径(現状、円マスクでの配置のみ対応)
        """
        width = ellipse_radius * 2
        height = ellipse_radius * 2
        left = center[0] - ellipse_radius
        top = center[1] - ellipse_radius
        style = OrderedDict()
        style['background'] = 'url({}) center'.format(layer_image_url)
        style['background-size'] = 'cover'
        style['border-radius'] = '{}px'.format(ellipse_radius)
        style['width'] = self.to_pixel(width)
        style['height'] = self.to_pixel(height)
        style['position'] = 'absolute'
        style['left'] = self.to_pixel(left)
        style['top'] = self.to_pixel(top)
        style['z-index'] = str(self.z_index)

        clip_rect = [0, width, height, 0]
        if top < 0:
            clip_rect[0] = abs(top)
        if left < 0:
            clip_rect[3] = abs(left)

        overflow_x = left + width - self.width
        if overflow_x > 0:
            clip_rect[1] = width - overflow_x
        overflow_y = top + height - self.height
        if overflow_y > 0:
            clip_rect[2] = height - overflow_y

        style['clip'] = 'rect({})'.format(' '.join([self.to_pixel(x) for x in clip_rect]))

        html = '<div {} >&nbsp;</div>'.format(self.style_attr(style))
        self.htmls.append(html)
        self.z_index += 1

    def style_attr(self, style_dict):
        return 'style="{}"'.format(';'.join(['{}:{}'.format(k, v) for k, v in style_dict.iteritems()]))

    def output(self):
        style = OrderedDict()
        style['width'] = self.to_pixel(self.width)
        style['height'] = self.to_pixel(self.height)
        style['position'] = 'relative'
        style['background'] = '#000000;'
        return '<div {style} >\n{inner}</div>'.format(style=self.style_attr(style), inner='\n'.join(self.htmls))

    @classmethod
    def to_pixel(cls, quantity):
        return '{}px'.format(quantity)
