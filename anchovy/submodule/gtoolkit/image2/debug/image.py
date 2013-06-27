# -*- coding:utf-8 -*-
from StringIO import StringIO
import logging
from PIL import Image as PIL_Image, ImageDraw
from hashlib import sha1
from django.utils.functional import cached_property
from ..exceptions import ImageValidationError
from gsocial.templatetags.osmobile import opensocial_session_url_convert
from ..image import Image, FORMAT

DUMMIES = {

}


class DebugImage(Image):
    def __init__(self, *args, **kwargs):
        super(DebugImage, self).__init__(*args, **kwargs)
        self.dummy_image = None
        try:
            self.is_valid()

        except ImageValidationError as exception:
            # cache
            dummy_key = sha1(super(DebugImage, self).url).hexdigest()
            logging.debug(u'{}:{} DummyKey:{}'.format(
                exception.__class__.__name__, exception.message, dummy_key))
            if dummy_key not in DUMMIES:
                DUMMIES[dummy_key] = self

            self.dummy_image = DummyImage(exception, dummy_key, *args, **kwargs)

    @property
    def url(self):
        if self.dummy_image:
            return self.dummy_image.url

        return super(DebugImage, self).url

    @property
    def pil_image(self):
        """
        画像をPILでロードして返す
        """
        if self.dummy_image:
            return self.dummy_image.pil_image

        return super(DebugImage, self).pil_image

    @cached_property
    def media(self):
        """
        画像のバイナリデータを返す
        """
        if self.dummy_image:
            return self.dummy_image.media

        return super(DebugImage, self).media


class DummyImage(Image):
    def __init__(self, exception, dummy_key, *args, **kwargs):
        super(DummyImage, self).__init__(*args, **kwargs)
        self.exception = exception
        self.dummy_key = dummy_key

    @property
    def url(self):
        return opensocial_session_url_convert(
            '/debug_image/{}/'.format(self.dummy_key))

    @property
    def pil_image(self):
        """
        画像をPILでロードして返す
        """
        img = PIL_Image.new('RGBA', (self.format.width, self.format.height),
                            self.exception.dummy_color)
        draw = ImageDraw.Draw(img)
        draw.text((1, 1), '{}'.format(self.instance.pk), fill='#000000')
        draw.text((1, 14),
                  '{}'.format(self.instance.__class__.__name__),
                  fill='#000000')
        draw.text((1, 28),
                  '{}'.format(self.exception.message),
                  fill='#000000')
        draw.text((1, 52),
                  '{}'.format(self.exception.__class__.__name__),
                  fill='#000000')
        return img

    @property
    def media(self):
        output = StringIO()
        self.pil_image.save(output, FORMAT.get(self.format.ext,
                                               'PNG'), quality=95)
        return output.getvalue()
