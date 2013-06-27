# -*- coding:utf-8 -*-
from django import template
from django.utils.encoding import smart_str
from gtoolkit.image.image import Image as Image1
from ..device import get_image_url
from ..mixins import Image, ImageManager


register = template.Library()


@register.simple_tag
def image_url(image_or_manager=None, label=None):
    u"""
    画像用URLを出力する

    引数が無い場合、画像URLのプレフィックスを返す。

    :param image_or_manager:
    :param label:
    例::

        <img src="{% image_url %}/common/line_gold_small.gif" />

    引数にImageMixinが出力するイメージマネージャなどを渡すと、そのイメージマネージャの
    該当ラベルのついた画像 URL を出力する。

    例::

        <img src="{% image_url player.guild.master.leader_card.card.image.icon %}" />
        <img src="{% image_url player.guild.master.leader_card.card.image 'icon' %}" />
    """
    image = None
    if isinstance(image_or_manager, ImageManager) and label:
        # マネージャーとラベル名が渡された
        image = image_or_manager[smart_str(label)]

    if isinstance(image_or_manager, (Image, Image1)):
        # Imageを直接渡されている
        image = image_or_manager

    if image:
        return image.url

    return get_image_url()
