# -*- coding: utf-8 -*-
"""
Gree Share Service要templatetags
templatetags share_service
"""

from django import template
from django.utils.encoding import smart_unicode

register = template.Library()

SHARE_SERVICE_TEMPLATE_PATH =  'opensocial/share_service.html'
INVITE_SERVICE_TEMPLATE_PATH = 'opensocial/invite_service.html'
UPGRADE_SERVICE_TEMPLATE_PATH = 'opensocial/upgrade.html'


@register.inclusion_tag(SHARE_SERVICE_TEMPLATE_PATH)
def share_service(value, callback_url, message=None, img_url_640=None,
        img_url_240=None,img_url_75=None):
    u"""
    ひとことサービスのボタンを出す

    使い方::

        {% share_service <ボタン文言> <戻りURL> [送信メッセージ] [画像URL640] [画像URL240] [画像URL75] %}

    * 送信メッセージは119文字以内です
    * 各画像URLは、不要な場合は指定しないか None にしてください
    """
    res = {
        'callback_url': callback_url,
        'message': smart_unicode(message),
        'value': value,
        'img_url_640': img_url_640,
        'img_url_240': img_url_240,
        'img_url_75': img_url_75,
    }
    return res


@register.inclusion_tag(INVITE_SERVICE_TEMPLATE_PATH)
def invite_service(value, callback_url, to_user_ids, message=None):
    u"""
    招待サービスのボタンを出す

    使い方::

        {% invite_service <ボタン文言> <戻りURL> <送信ユーザーIDのリスト> [送信メッセージ] %}

    * 送信ユーザーIDのリスト は 15件までです
    * 送信メッセージは 100Byte 以内です
    """
    res = {
        'callback_url': callback_url,
        'to_user_ids': to_user_ids,
        'message': smart_unicode(message),
        'value': value,
    }
    return res


@register.inclusion_tag(UPGRADE_SERVICE_TEMPLATE_PATH)
def upgrade_service(value, grade, callback_url):
    u"""
    アップグレードサービスのボタンを出す

    ユーザーグレードの更新を促す。

    使い方::

        {% upgrade_service <ボタン文言> <目標ユーザーグレード> <戻りURL> %}
    """
    res = {
        'callback_url': callback_url,
        'grade': grade,
        'value': value,
    }
    return res
