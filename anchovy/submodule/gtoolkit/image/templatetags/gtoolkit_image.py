# -*- coding:utf-8 -*-
from django import template
from django.utils.encoding import smart_str
from gtoolkit.image import Image, get_static_url, get_image_url
from gtoolkit.image2.image import Image as Image2


register = template.Library()


@register.simple_tag
def static_url():
    u"""
    静的ファイル用URLを出力する
    使われていないようだ
    """
    return get_static_url()


@register.simple_tag
def image_url(image_manager=None, label=None):
    u"""
    画像用URLを出力する

    引数が無い場合、画像URLのプレフィックスを返す。

    :param image_manager:
    :param label:
    例::

        <img src="{% image_url %}/common/line_gold_small.gif" />

    引数に image_manager, label を渡すと、そのイメージマネージャの
    該当ラベルのついた画像 URL を出力する。

    例::

        <img src="{% image_url player.guild.master.leader_card.card.image 'icon' %}" />
    """
    if image_manager and label:
        image = image_manager[smart_str(label)]
        if image:
            return image.url

    if isinstance(image_manager, (Image, Image2)):
        # Imageを直接渡されている
        return image_manager.url

    return get_image_url()


@register.inclusion_tag('common/parts/image.html')
def image(image_manager=None, label=None):
    u"""
    イメージマネージャから該当ラベルの画像を、<img ...>タグごと出力する

    外部テンプレート: common/parts/image.html

    例::

        {% image boss_deck.player_cards.4.card.image 'icon' %}
    """
    if image_manager and label:
        # ImageManagerとlabel
        image = image_manager[smart_str(label)]
        return {
            'image_url': get_image_url() + '/' + image.path,
            'width': image.format.view_width,
            'height': image.format.view_height,
        }

    if isinstance(image_manager, (Image, Image2)):
        # Image
        return {
            'image_url': get_image_url() + '/' + image_manager.path,
            'width': image_manager.format.view_width,
            'height': image_manager.format.view_height,
        }

    return {
        'image_url': get_image_url(),
        'width': None,
        'height': None,
    }


@register.simple_tag
def image_attr(image_manager=None, label=None):
    """
    IMGタグ用のattrを出力する
    """
    src = ''
    html = ''
    width = 0
    height = 0
    if image_manager and label:
        # ImageManagerとlabel
        image = image_manager[smart_str(label)]
        src = get_image_url() + '/' + image.path
        width = image.format.view_width
        height = image.format.view_height
    if isinstance(image_manager, (Image, Image2)):
        # Image
        src = get_image_url() + '/' + image_manager.path
        width = image_manager.format.view_width
        height = image_manager.format.view_height
    html += u' src="{}" '.format(src) if src else ''
    html += u' width="{}" '.format(width) if width else ''
    html += u' height="{}" '.format(height) if height else ''
    return html
