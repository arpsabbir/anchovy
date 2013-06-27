# -*- coding:utf-8 -*-
import os
from django.conf import settings
from gtoolkit import simple_join_url
from mobilejp.middleware.mobile import get_current_device


FEATUREPHONE_DEVICE = 'featurephone'
SMARTPHONE_DEVICE = 'smartphone'

IMAGE_ROOT_PATH = os.path.join(settings.MEDIA_ROOT, 'images')
IMAGE_BASE_URL = simple_join_url(settings.STATIC_URL, 'images/')


def get_image_url(device_name=None):
    return simple_join_url(IMAGE_BASE_URL,
                           get_device_image_dir_name(name=device_name))


class BaseDevice(object):
    _image_dir_name = None
    _shortcut_name = None

    def __init__(self, mobilejp_device=None):
        self.device = mobilejp_device

    @classmethod
    def check(cls, mobilejp_device):
        raise NotImplementedError

    @property
    def image_dir_name(self):
        return self._image_dir_name

    @property
    def shortcut_name(self):
        return self._shortcut_name


class FeaturePhoneDevice(BaseDevice):
    _image_dir_name = FEATUREPHONE_DEVICE
    _shortcut_name = 'fp'

    @classmethod
    def check(cls, mobilejp_device):
        return mobilejp_device.is_featurephone


class SmartPhoneDevice(BaseDevice):
    _image_dir_name = SMARTPHONE_DEVICE
    _shortcut_name = 'sp'

    @classmethod
    def check(cls, mobilejp_device):
        return mobilejp_device.is_smartphone


class UnknownDevice(SmartPhoneDevice):
    @classmethod
    def check(cls, mobilejp_device):
        return True


DEVICE_NAME_MAP = {
    FEATUREPHONE_DEVICE: FeaturePhoneDevice,
    SMARTPHONE_DEVICE: SmartPhoneDevice,
}


def get_device_image_dir_name(name=None, mobilejp_device=None):
    device = get_device(name=name, mobilejp_device=mobilejp_device)
    return device.image_dir_name


def get_device(name=None, mobilejp_device=None):
    """
    mobilejp内のデバイスオブジェクトからImage用のデバイスオブジェクトを返す

    :param mobilejp_device:
    :return:
    """
    if name in DEVICE_NAME_MAP:
        return DEVICE_NAME_MAP[name]()

    if not mobilejp_device:
        # 指定が無ければ現在のデバイスを取得
        mobilejp_device = get_current_device()

    # mobilejpのdeviceクラスから検索
    if mobilejp_device:
        for device_class in BaseDevice.__subclasses__():
            if device_class.check(mobilejp_device):
                return device_class(mobilejp_device)

    # 該当デバイス無し
    return UnknownDevice(mobilejp_device)
