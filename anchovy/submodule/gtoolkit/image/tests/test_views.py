# -*- coding: utf-8 -*-

from mock import Mock
from unittest import TestCase


class MockResponse(dict):
    def write(self, data):
        self._data = data


class MockPILImage(object):
    def save(self, buf, *args, **kwargs):
        buf.write('test')


import gtoolkit.image.views

gtoolkit.image.views.http = Mock(HttpResponse=MockResponse)

from gtoolkit.image.views import PILImageView, PILImageLayerMixin, \
    ImageFileDoesNotExistsError, Image, ImageLayerTag


class ImageViewTest(TestCase):
    def test_pil_image_view(self):
        class TestPilImageView(PILImageView):
            def get_pil_image(self, request):
                return MockPILImage()

        mock_request = Mock()
        view = TestPilImageView()
        response = view.get(mock_request)
        self.assertEqual(response._data, 'test')

    def test_pil_image_layer_mixin(self):
        m = PILImageLayerMixin()
        mock_image = Mock()
        m.set_image(mock_image)
        self.assertEqual(m.get_image(), mock_image)
        m.initialize_image('RGBA', (100, 100,))

        self.assertRaises(ImageFileDoesNotExistsError, m.layer_image, '')
        layer_image = m._image.copy()
        layer_image = m.mask_ellipse(layer_image)
        m._simple_layer_image(layer_image)
        self.assertIsInstance(m._image, Image.Image)

    def test_image_layer_tag(self):
        i = ImageLayerTag(100, 100)
        i.layer_image('http://example.com/image1')
        i.layer_image_ellipse('http://example.com/image2', (50, 50,), 30)
        html = i.output()
        self.assertIn('http://example.com/image1', html)
        self.assertIn('http://example.com/image2', html)
        self.assertIn('z-index', html)
        self.assertIn('<div', html)