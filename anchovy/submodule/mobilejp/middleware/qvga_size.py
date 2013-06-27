# -*- coding: utf-8 -*-
"""
>>> _replace_html('<img style="width:60px; height:40px;" />')
'<img style="width:120px; height:80px;" />'

>>> _replace_html('<img width="240" height="160" />')
'<img width="480" height="320" />'

>>> _replace_html('<img src="example.png" style="width:100%" height="30" />')
'<img src="example.png" style="width:100%" height="60" />'

>>> _replace_html('<img src="example.png" width="100%" height="30%" />')
'<img src="example.png" width="100%" height="30%" />'

"""
import re
from mobilejp.log import logger


RE_QVGA_SIZE = re.compile(
    r'(width|height)(\s*:\s*|=)([\"\']*)(?P<value>\d+)(?P<unit>px|%|)([\"\']*)',
    re.I)


def _replace_callback(m):
    """
    文字列結合の速度:

        %s で連結する場合: 2000 microseconds
        .format(): 2000 microseconds
        ''.join: 1800 microseconds
        どれもそれほど変わりない

    :param m:
    """
    value = int(m.group('value'))
    if not m.group('unit') == '%':
        # 単位が % 以外は2倍にする
        value *= 2
    return ''.join(
        (m.group(1), m.group(2), m.group(3),
         str(value), m.group(5), m.group(6)))


def _replace_html(source):
    return RE_QVGA_SIZE.sub(_replace_callback, source)


class QvgaSizeMiddleware(object):
    """
    
    width:60px
    height="200"
    
    などを検出して、VGA機ならサイズを2倍にする
    
    """

    def process_response(self, request, response):
        logger.debug('qvga_size_response')

        if not request.path.startswith("/m/"):
            return response

        content_type = response.get('Content-Type', "")
        if not content_type.startswith("text/html"):
            return response

        if not hasattr(request, 'device'):
            return response

        if not hasattr(request.device.detect, 'display'):
            return response

        if not request.device.detect.display.is_vga():
            return response

        #VGA対応端末なので適用
        content = response.content
        response.content = _replace_html(content)
        return response
