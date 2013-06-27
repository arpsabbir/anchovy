# -*- coding:utf-8 -*-

from mock import Mock

MOCK_DEVICE = 'featurephone'
MOCK_IMAGE_URL = '/static/images/featurephone'
MOCK_SETTINGS = {
    'STATIC_URL': '/static',
    'MEDIA_ROOT': '/media/root/path/',
}

import gtoolkit.image2.device

gtoolkit.image2.device.get_device_image_dir_name = Mock(return_value=MOCK_DEVICE)
gtoolkit.image2.device.get_image_url = Mock(return_value=MOCK_IMAGE_URL)

import os
from unittest import TestCase

from gtoolkit.image2.mixins import image, image_manager, label, ImageMixin


class Obj(ImageMixin):
    image_path_format = os.path.join('{base_name}', '{id}', '{label}.{ext}')
    _image_manager = image_manager(
        image('large', extend_base_path=['FP'],ext='png', width=640, height=960),
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
            label('large', alias='SP.large'),
            label('medium', alias='medium'),
            label('small', alias='small'),
        ),
    )

    def __init__(self, pk):
        self.id = self.pk = pk


class ImageTest(TestCase):
    def test_image_url(self):
        obj = Obj(3)
        self.assertEqual(obj.image.large, 'image2_obj/3/large.png')
        self.assertEqual(obj.image.url, '/static/images/featurephone')
