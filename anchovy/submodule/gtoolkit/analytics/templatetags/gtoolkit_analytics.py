# -*- coding: utf-8 -*-
import random
import hashlib
import urllib
from django import template
from django.conf import settings
from gtoolkit.image.static_switcher import get_device_name

register = template.Library()


@register.simple_tag
def google_analytics(request, player):
    u"""
    GoogleAnalytics用のタグを出す

    使い方::

        {% google_analytics <request> <player> %}
    """
    if not settings.ANALYTICS_ID:
        return ''

    user_id = player.id if player.id else str(random.randint(1000000000, 9999999999))
    utmvid = hashlib.md5(user_id).hexdigest()

    if 'HTTP_REFERER' in request.META and request.META['HTTP_REFERER'] != '':
        http_referer = request.META['HTTP_REFERER']
    else:
        http_referer = '-'
    http_referer = http_referer.split('?')[0]

    device = get_device_name()
    params = {
        'utmac': settings.ANALYTICS_ID,
        'utme': '8(device*player)9(%s*%s)11(2,2)' % (device, user_id),
        'utmhn': urllib.quote('mgadget.gree.jp'),
        'utmn': str(random.randint(0, 0x7fffffff)),
        'utmp': urllib.quote(request.path),
        'utmr': urllib.quote(http_referer),
        'utmvid': utmvid[:16],
    }

    tag = '<img src="http://www.google-analytics.com/__utm.gif' + \
            '?utmwv=4.4sh' + \
            '&utmac=%(utmac)s' + \
            '&utmhn=%(utmhn)s' + \
            '&utmn=%(utmn)s' + \
            '&utmp=%(utmp)s' + \
            '&utmr=%(utmr)s' + \
            '&utmvid=0x%(utmvid)s' + \
            '&utmcc=__utma%%3D999.999.999.999.999.1%%3B' + \
            '&guid=ON" border="0" width="0" height="0" />'

    return tag % params
