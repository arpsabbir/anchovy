# -*- coding: utf-8 -*-

from mock import Mock

MOCK_DEVICE = 'featurephone'
MOCK_IMAGE_URL = '/static/images/featurephone'
MOCK_SETTINGS = {
    'STATIC_URL': '/static',
    'MEDIA_ROOT': '/media/root/path/',
}

import gtoolkit.image.static_switcher
gtoolkit.image.static_switcher.get_device_name = Mock(return_value=MOCK_DEVICE)
gtoolkit.image.static_switcher.get_image_url = Mock(return_value=MOCK_IMAGE_URL)
gtoolkit.image.static_switcher.settings = Mock(**MOCK_SETTINGS)

import gtoolkit.image.image
gtoolkit.image.image.get_device_name = Mock(return_value=MOCK_DEVICE)
gtoolkit.image.image.get_image_url = Mock(return_value=MOCK_IMAGE_URL)


import os
from unittest import TestCase
from gtoolkit.image.image import Image, ImageFormat

class ImageTest(TestCase):
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

    def test_init(self):
        self.assertIsInstance(ImageFormat('jpg', 20, 20), ImageFormat)
        self.assertIsInstance(Image('/static/image/test.jpg', ImageFormat('jpg', 20, 20)), Image)


    def test_image_format(self):

        width = 640
        height = 960
        view_width = 320
        view_height = 480

        # view系両方指定無し
        img_format = ImageFormat('jpg', width, height)
        self.assertIsInstance(img_format, ImageFormat)
        self.assertEqual(img_format.width, width)
        self.assertEqual(img_format.height, height)
        self.assertEqual(img_format.view_width, width)
        self.assertEqual(img_format.view_height, height)

        # view_widthだけ指定あり
        img_format = ImageFormat('jpg', width, height, view_width=view_width)
        self.assertIsInstance(img_format, ImageFormat)
        self.assertEqual(img_format.width, width)
        self.assertEqual(img_format.height, height)
        self.assertEqual(img_format.view_width, view_width)
        self.assertEqual(img_format.view_height, None)

        # view_heightだけ指定あり
        img_format = ImageFormat('jpg', width, height, view_height=view_height)
        self.assertIsInstance(img_format, ImageFormat)
        self.assertEqual(img_format.width, width)
        self.assertEqual(img_format.height, height)
        self.assertEqual(img_format.view_width, None)
        self.assertEqual(img_format.view_height, view_height)

        # 全指定あり
        img_format = ImageFormat('jpg', width, height, view_width=view_width, view_height=view_height)
        self.assertIsInstance(img_format, ImageFormat)
        self.assertEqual(img_format.width, width)
        self.assertEqual(img_format.height, height)
        self.assertEqual(img_format.view_width, view_width)
        self.assertEqual(img_format.view_height, view_height)



    def test_image_url(self):
        img_format = ImageFormat('jpg', 640, 960)
        image = Image('card/11001011/icon.jpg', img_format)
        self.assertEqual(image.path, 'card/11001011/icon.jpg')
        self.assertEqual(image.absolute_path, '/media/root/path/images/featurephone/card/11001011/icon.jpg')
        self.assertEqual(image.url, '/static/images/featurephone/card/11001011/icon.jpg')

        self.assertEqual(image.format.width, 640)
        self.assertEqual(image.format.height, 960)
