# -*- coding: utf-8 -*-
import os
from django.conf import settings
from mobilejp.middleware.mobile import get_current_device
from gtoolkit import simple_join_url

DEVICE_NAME_FEATUREPHONE='featurephone'
DEVICE_NAME_SMARTPHONE='smartphone'

def get_static_url():
    return settings.STATIC_URL

def get_image_url(device_name=None):
    return simple_join_url(settings.STATIC_URL, 'images/' + (
        device_name if device_name else get_device_name()
    ))

def get_image_path(device_name=None):
    if device_name is None:
        device_name = get_device_name()
    return os.path.join(settings.MEDIA_ROOT, 'images', device_name)

def get_device_name(is_featurephone=None):
    """
    静的ファイル用のデバイス区分名
    """

    if is_featurephone is None:
        # Noneならアクセスしているデバイスから取得
        is_featurephone = get_current_device().is_featurephone

    if is_featurephone:
        return DEVICE_NAME_FEATUREPHONE
    else:
        return DEVICE_NAME_SMARTPHONE

def context_processor(request):
    """
    デバイスに応じた静的ファイル用URLヘのURLを渡す
    """
    return {
        'STATIC_URL': get_static_url(),
        'IMAGE_URL' : get_image_url(),
    }
