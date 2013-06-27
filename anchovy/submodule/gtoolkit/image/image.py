# -*- coding: utf-8 -*-
import os
from django.conf.urls import include
from gtoolkit.cache.memoized_property import memoized_property
from gtoolkit.image.static_switcher import get_image_path, get_image_url, get_device_name


class BaseImageValidationError(Exception):
    pass


class ImageDoesNotExist(BaseImageValidationError):
    """
    画像が無い
    """


class InvalidImageSizeError(BaseImageValidationError):
    """
    画像サイズが違う
    """


class InvalidImageProgressiveError(BaseImageValidationError):
    """
    画像がプログレッシブ
    """


class ImageFormat(object):
    """
    画像のファイルフォーマットやサイズ情報などを管理
    """
    def __init__(self, ext, width, height, view_width=None, view_height=None,
                 optional=False, optional_if_in=None, check_progressive=False):
        """
        必要データを受け取って初期化

        :param str ext: 拡張子
        :param int width: 実画素数・横
        :param int height: 実画素数・縦
        :param int view_width: 表示での論理画素数・横
        :param int view_height: 表示での論理画素数・縦
        :param bool optional: 必要でない場合True
        :param list optional_if_in: リストで指定したラベルがどれか存在する場合は無くても良い
        :param bool check_progressive: JPEGでプログレッシブ画像かチェックするか
        """
        self.ext = ext
        self.width = width
        self.height = height
        self._view_width = view_width
        self._view_height = view_height
        self.optional = optional
        self.optional_if_in = optional_if_in
        self.check_progressive = check_progressive

    @property
    def view_width(self):
        """
        表示サイズ: 横幅 [px]

        view_heightが指定されている場合は省略され、それ以外は実サイズを返す
        """
        if self._view_width:
            # 指定があるのでそのまま返す
            return self._view_width

        if self._view_height:
            # 縦が指定されているので、ブラウザに自動計算させるため省略
            return

        return self.width

    @property
    def view_height(self):
        """
        表示サイズ: 縦幅 [px]

        view_widthが指定されている場合は省略され、それ以外は実サイズを返す
        """
        if self._view_height:
            # 指定があるのでそのまま返す
            return self._view_height

        if self._view_width:
            # 横が指定されているので、ブラウザに自動計算させるため省略
            return

        # 実サイズ
        return self.height


class ImageLabelAlias(object):
    def __init__(self, target_label, target_is_featurephone=None):
        """
        :param target_label: 画像ラベル名
        :type target_label: string

        :param target_is_featurephone: FP用画像のラベルを使う。Noneの場合は同一デバイス
        :type target_is_featurephone: bool
        """
        self.target_label = target_label
        self.target_is_featurephone = target_is_featurephone

    @property
    def is_device_designated(self):
        """
        デバイス指定があるかどうか
        """
        return self.target_is_featurephone is not None


class Image(object):
    """
    単体画像を管理するクラス
    """

    def __init__(self, image_path, image_format, device_name=None):
        """
        :param str image_path: 各端末用ディレクトリから画像へのパス
        :param ImageFormat image_format: 画像設定データ
        :param bool device_name: 対象端末
        """
        self.image_path = image_path
        self.image_format = image_format
        self._device_name = device_name

    def __repr__(self):
        return self.path

    def __str__(self):
        return self.path

    @property
    def absolute_path(self):
        """
        画像への絶対パスを返す
        """
        return self.get_absolute_path(self._device_name if self._device_name else None)

    @property
    def path(self):
        """
        画像へのIMAGE_URLからの相対パスを返す
        """
        return self.image_path

    @property
    def url(self):
        """
        画像へのURLを返す
        """
        return '{IMAGE_URL}/{IMAGE_PATH}'.format(IMAGE_URL=get_image_url(self._device_name), IMAGE_PATH=self.path)

    @memoized_property
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
        import os
        return os.path.exists(self.absolute_path)

    @memoized_property
    def pil_image(self):
        """
        画像をPILでロードして返す
        """
        from PIL import Image as PIL_Image
        return PIL_Image.open(self.absolute_path)

    def is_valid(self, image_manager=None, check_optional_if_in=True):
        """
        ファイルが正しいかどうかを返す

        :param ImageManager image_manager: optional_if_inを判別する為に他の画像使いたい場合用
        :param bool check_optional_if_in: optional_if_inをチェックする
        """

        if self.is_exists:
            # 存在する

            # 画像サイズチェック
            if not self._check_image_size():
                raise InvalidImageSizeError(
                    "O {}:{} -> X {}:{} [{}]".format(
                        self.image_format.width,
                        self.image_format.height,
                        self.pil_image.size[0],
                        self.pil_image.size[1],
                        self.absolute_path
                    )
                )

            # プログレッシブ画像チェック
            if not self._check_progressive():
                raise InvalidImageProgressiveError(
                    "{}".format(
                        self.absolute_path
                    )
                )

            # OK
            return True

        else:
            # 存在しない

            if self.image_format.optional:
                # オプションなら無くても良い
                return True

            if check_optional_if_in and self.image_format.optional_if_in and isinstance(image_manager, ImageManager):
                # optional_if_inのラベルのうちどれかがあればこれは無くても良い
                for image_label in self.image_format.optional_if_in:
                    if image_manager[image_label].is_valid(check_optional_if_in=False):
                        # あったのでOK
                        return True

            raise ImageDoesNotExist(
                "{}".format(
                    self.absolute_path
                )
            )

    def get_absolute_path(self, device_name=None):
        """
        画像の絶対パスを取得
        """
        return os.path.join(get_image_path(device_name), self.image_path)

    def _check_progressive(self):
        """
        JPEGのプログレッシブ画像かチェックする
        """
        return not (self.image_format.check_progressive
                    and self.pil_image.info.has_key('progression')
                    and self.pil_image.info['progression'] == 1)

    def _check_image_size(self):
        """
        画像のサイズチェック
        """
        return (self.pil_image.size[0] == self.image_format.width)\
                and (self.pil_image.size[1] == self.image_format.height)


class ImageManager(object):
    """
    複数画像を管理するクラス

    ラベル名から単体画像用のクラスを返す
    """

    def __init__(self, image_path_format, image_path_params, image_format_map, device_name=None):
        self.image_path_format = image_path_format
        self.image_path_params = image_path_params
        self._image_format_map = image_format_map
        self._device_name = device_name

    def __getattr__(self, item):
        return self.get_image(item)

    def __getitem__(self, item):
        return self.get_image(item)


    @property
    def image_format_map(self):
        """
        デバイスに対応したフォーマット表を返す
        """
        return self._image_format_map[self._get_device_name()]

    @property
    def labels(self):
        return self.image_format_map.keys()

    def _get_device_name(self, is_featurephone=None):
        return self._device_name if self._device_name else get_device_name(is_featurephone)


    def get_image(self, label):
        """
        画像オブジェクト作成

        :param string label: 画像ラベル名
        """
        if label == 'labels':
            return self.labels

        if label in ['sp', 'fp']:
            return self.get_manager(is_featurephone = (label == 'fp'))

        image_format = self.get_image_format(label)
        if image_format:

            if isinstance(image_format, ImageLabelAlias):
                # 他ラベルへのエイリアス
                if image_format.is_device_designated:
                    # デバイス指定があるのでマネージャーを切り替えて取得
                    return self.get_manager(
                        is_featurephone=image_format.target_is_featurephone,
                    ).get_image(image_format.target_label)

                return self.get_image(image_format.target_label)

            return Image(
                image_path=self.get_path(
                    label=label,
                    ext=image_format.ext,
                ),
                image_format=image_format,
                device_name=self._device_name
            )

        return None

    def get_manager(self, is_featurephone=None):
        return ImageManager(
            self.image_path_format,
            self.image_path_params,
            self._image_format_map,
            device_name=get_device_name(is_featurephone)
        )

    def get_path(self, **kwargs):
        """
        画像へのパスを生成する
        """
        params = self.image_path_params
        params.update(kwargs)
        return self.image_path_format.format(**params)


    def get_image_format(self, label, attr_name=None):
        """
        指定ラベルのデバイスに応じた画像情報を返す
        :param string label: 画像ラベル名
        :param string attr_name: 対象フォーマットの特定情報が欲しい場合に指定
        """

        if label not in self.image_format_map:
            return None

        image_format = self.image_format_map[label]

        if isinstance(attr_name, str) and hasattr(image_format, attr_name):
            return getattr(image_format, attr_name)

        return image_format


class ImageMixin(object):
    """
    画像用のプロパティを追加するMixinクラス

    image_path_format
      画像のパス構造を設定して下さい。
      /card/カードID/サイズ名.拡張子のような構造の場合は
      {base_name}/{id}/{label}.{ext}のように設定します。

    image_format_map
      画像のファイルフォーマット、拡張子、サイズなどを種類ごとに渡します。
      以下のような構造にします。
      {
        デバイス名: {
          ラベル名: ImageFormat(..),
          ラベル名: ImageFormat(..),
        }
      }

    """

    image_path_format = os.path.join('{base_name}', '{id}', '{label}.{ext}')
    image_format_map = {
        'smartphone': {
            'large': ImageFormat(ext='png', width=640, height=960, view_width=320),
            'medium': ImageFormat(ext='png', width=320, height=480),
            'small': ImageFormat(ext='png', width=160, height=240),
            },
        'featurephone': {
            'large': ImageFormat(ext='jpg', width=320, height=480),
            'medium': ImageFormat(ext='jpg', width=160, height=240),
            'small': ImageFormat(ext='jpg', width=40, height=60),
            },
        }

    @property
    def image(self):
        return ImageManager(
            self.image_path_format,
            self.get_image_path_base_params(),
            self.image_format_map)


    def get_image_path_base_params(self):
        try:
            app_label = self._meta.app_label
        except AttributeError:
            app_label = self.__module__.split('.')[-2]

        return {
            'base_name': app_label + '_' + self.__class__.__name__.lower(),
            'id': self.pk,
            }


def load_image_format_map(path, class_name, default_map):
    """
    image_format_map を extensionに定義がある場合に上書きする
    :param str path: moduleのパス
    :param str class_name: ImageMixinを継承しているクラスの名前
    :param dict default_map: ImageMixinを継承したクラスのimage_format_map

    :使い方
    from gtoolkit.image import ImageMixin, ImageFormat, load_image_format_map
    image_format_map = load_image_format_map(__name__, "ClassName", {
        "device_name":{"image_size":ImageFormat()}
    })
    """
    try:
        module_obj = include('extension.' + path)[0]
        image_mixin_child = getattr(module_obj, class_name)
        ex_map = image_mixin_child.image_format_map
        for device_type, maps in ex_map.iteritems():
            default_map[device_type].update(maps)
        return default_map

    except ImportError:
        return default_map
    except AttributeError:
        return default_map
