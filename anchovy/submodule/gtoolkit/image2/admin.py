# -*- coding:utf-8 -*-
from __future__ import unicode_literals

IMAGE_TD_TAG = '</td><td>'
IMAGE_TAG = """
<div style="width:{WIDTH}px;" onclick="javascript:$('img#{NAME}').css('position', 'absolute').removeAttr('width').css('z-index', 110);"
 onmouseout="javascript:$('img#{NAME}').css('z-index', 0).css('position', 'static').attr('width', $('img#{NAME}').attr('default-width'));">
<img id="{NAME}" src="{SRC}" width="{IMAGE_WIDTH}" default-width="{DEFAULT_WIDTH}" />
</div>
"""
DEFAULT_WIDTH = 80


class ImageAdminMixin(object):
    """
    ImageMixinを使用しているクラスのDjangoAdminページで画像一覧を出すためのMixinクラス
    """
    def images(self, obj):
        labels = []
        image_tags = []

        for image_name, image in obj.image.images.items():

            if not image.dummy_image and not image.is_exists:
                continue

            name = self._get_name(obj, image_name)
            labels.append(image_name)
            width = DEFAULT_WIDTH
            if int(image.format.view_width) < DEFAULT_WIDTH:
                width = image.format.view_width

            image_tags.append(
                IMAGE_TAG.replace('\n', '').format(
                    WIDTH=DEFAULT_WIDTH, NAME=name, SRC=image.url,
                    IMAGE_WIDTH=width, DEFAULT_WIDTH=width)
            )

        return """
        <table>
            <tr><td style="width:{WIDTH}px;">{LABELS}</td></tr>
            <tr><td style="width:40px;">{IMAGES}</td></tr>
        </table>""".format(
            WIDTH=DEFAULT_WIDTH,
            LABELS='</td><td style="width:{WIDTH}px;">'.format(
                WIDTH=DEFAULT_WIDTH).join(labels),
            IMAGES=IMAGE_TD_TAG.join(image_tags),
        ).replace('\n', '')

    def _get_name(self, obj, image_name):
        return '{}_{}'.format(obj.pk, image_name).replace('.', '_')

    images.short_description = 'images'
    images.allow_tags = True
