# -*- coding:utf-8 -*-
from gtoolkit.image.image import BaseImageValidationError

class ImageAdminMixin(object):
    """
    ImageMixinを使用しているクラスのDjangoAdminページで画像一覧を出すためのMixinクラス
    """
    def images(self, obj):
        labels = list(set(obj.image.sp.labels + obj.image.fp.labels))
        return u'<table><tr><td>label</td>{LABELS}</tr><tr><td>SP</td>{SP}</tr><tr><td>FP</td>{FP}</tr></table>'.format(
            LABELS=u''.join(['<td>{LABEL}</td>'.format(LABEL=label) for label in labels]),
            SP=u''.join([img(obj.pk, obj.image.sp, label) for label in labels]),
            FP=u''.join([img(obj.pk, obj.image.fp, label) for label in labels])
        )
    images.short_description = 'images'
    images.allow_tags = True

def img(id, mgr, label):
    """

    :param mgr:
    :param label:
    :return:
    """
    image = mgr[label]

    if not image:
        return '<td></td>'

    def print_img(error=False):
        name = '{}_{}_{}'.format(id, mgr._device_name, label)
        if error:
            base = '<td style="background-color:red; width:{WIDTH}px;"><img id="{NAME}" src="" style="width:{WIDTH}px;" /></td>'
        else:
            base = '<td style="width:{WIDTH}px;" onmouseover="javascript:$(\'img#{NAME}\').css(\'position\', \'absolute\').removeAttr(\'width\').css(\'z-index\', 110);" onmouseout="javascript:$(\'img#{NAME}\').css(\'z-index\', 0).css(\'position\', \'static\').attr(\'width\', $(\'img#{NAME}\').attr(\'default-width\'));"><img id="{NAME}" src="{SRC}" width="{WIDTH}" default-width="{WIDTH}" /></td>'

        return base.format(
            WIDTH=40 if int(image.format.view_width) > 40 else image.format.view_width,
            SRC=image.url,
            NAME=name
        )

    if image.is_exists:
        return print_img()

    try:
        image.is_valid(mgr)
    except BaseImageValidationError:
        return print_img(error=True)

    return ''


