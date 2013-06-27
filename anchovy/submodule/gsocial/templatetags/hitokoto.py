# -*- coding: utf-8 -*-
"""
templatetags
"hitokoto service" of GREE
ひとことサービス
"""
import os
import urllib

from django import template

register = template.Library()
abs_path = os.path.dirname(os.path.abspath(__file__))
file_path = abs_path + '/../templates/opensocial/hitokoto.html'
file_path_sp = abs_path + '/../templates/opensocial/hitokoto_sp.html'


@register.inclusion_tag(file_path)
def get_hitokoto_form(callbackurl, body_value, submit_value,
                      image_urls_640=None, image_urls_240=None, image_urls_75=None):
    u"""
    ひとことサービスのフォームを出す (フィーチャーフォン専用)

    Create the form for "hitokoto service" and return it.
    For feature phone.

    外部テンプレート: gsocial/templates/opensocial/hitokoto.html

    使い方::

        {% get_hitokoto_form <戻りURL> <ひとこと本文> <ボタン文言> [画像URL640] [画像URL240] [画像URL75] %}
    """
    #
    # Argument:
    #  callbackurl : Redirect url after the posting
    #  body_value : Content
    #  submit_value : The letters on submit button
    #  image_urls_640 : The url of 640px-size image
    #  image_urls_240 : The url of 240px-size image
    #  image_urls_75 : The url of 75px-size image
    # Return value:
    #  Return the form it creates（hitokoto.html）
    #
    # 引数
    #  callbackurl : ひとことを投稿後に遷移するURL
    #  body_value : 本文
    #  submit_value : 送信ボタンの文言
    #  image_urls_640 : 横640pxサイズの画像URL
    #  image_urls_240 : 横240pxサイズの画像URL
    #  image_urls_75 : 横75pxサイズの画像URL
    return {
        'callbackurl': callbackurl,
        'body_value': body_value,
        'submit_value': submit_value,
        'image_urls_640': image_urls_640,
        'image_urls_240': image_urls_240,
        'image_urls_75': image_urls_75,
        }

@register.inclusion_tag(file_path_sp)
def get_hitokoto_form_sp(callbackurl, body_value, submit_value,
                         image_urls_640=None, image_urls_240=None, image_urls_75=None):
    u"""
    ひとことサービスのフォームを出す (スマートフォン専用)

    Create the link for "hitokoto service" and return it.
    For smart phone.

    外部テンプレート: gsocial/templates/opensocial/hitokoto_sp.html

    使い方::

        {% get_hitokoto_form_sp <戻りURL> <ひとこと本文> <ボタン文言> [画像URL640] [画像URL240] [画像URL75] %}
    """
    # Argument:
    #  callbackurl : Redirect url after the posting
    #  body_value : Content
    #  submit_value : The letters on submit button
    #  image_urls_640 : The url of 640px-size image
    #  image_urls_240 : The url of 240px-size image
    #  image_urls_75 : The url of 75px-size image
    # Return value:
    #  Return the link it creates（hitokoto_sp.html）
    #
    # 引数
    #  callbackurl : ひとことを投稿後に遷移するURL
    #  body_value : 本文
    #  submit_value : 送信ボタンの文言
    #  image_urls_640 : 横640pxサイズの画像URL
    #  image_urls_240 : 横240pxサイズの画像URL
    #  image_urls_75 : 横75pxサイズの画像URL
    callbackurl = urllib.quote(callbackurl)

    return {
        'callbackurl': callbackurl,
        'body_value': body_value,
        'submit_value': submit_value,
        'image_urls_640': image_urls_640,
        'image_urls_240': image_urls_240,
        'image_urls_75': image_urls_75,
        }
