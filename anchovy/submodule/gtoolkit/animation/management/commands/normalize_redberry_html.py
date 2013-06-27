# -*- coding:utf-8 -*-
#import inspect
import datetime
import filecmp
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.encoding import smart_unicode, smart_str
from django.utils.functional import cached_property
#from gtoolkit.image import ImageMixin, ImageManager, DEVICE_NAME_FEATUREPHONE, DEVICE_NAME_SMARTPHONE
#from gtoolkit.image.image import BaseImageValidationError

import glob
import os
from gtoolkit.animation.render import ANIMATION_BASE_PATH

class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        redberry-1.0.12 以前のhtmlファイルを
        redberry-1.0.12 以降のhtmlに構造を近づけるバッチ
        """
        
        for path in html_files():
            fh = open(path)
            try:
                source = fh.read().decode(settings.FILE_CHARSET)
            finally:
                fh.close()
            
            print path
            version = get_redberry_version_from_source(source)

            print 'redberry-converter-version:', version

            if version == (0,0,0):
                continue

            if version < (1,0,12):
                source = insert_tags_1_0_11(source, version)
            elif version >= (1,0,12):
                source = insert_tags_1_0_12(source, version)

            fh = open(path, 'w')
            try:
                fh.write(source.encode(settings.FILE_CHARSET))
            finally:
                fh.close()






def html_files():

    directory = os.path.join(ANIMATION_BASE_PATH, 'html')
    filename = 'index.html'

    for root, dirs, files in os.walk(directory):
        for f in files:
            if f == filename:
                yield os.path.join(root, f)

def get_redberry_version_from_source(source):
    version = None

    # 1.0.12 以降
    m = re.search(r'{--redberry-converter-version:([\d\.]+)--}', source)
    if m:
        return tuple(int(s) for s in m.group(1).split('.'))

    # 1.0.11 以前
    m = re.search(r': redberry-([\d\.]+)', source)
    if m:
        return tuple(int(s) for s in m.group(1).split('.'))

    return (0,0,0)

def find_right(paturn, source):
    i = source.find(paturn)
    if i == -1:
        raise
    i += len(paturn)
    return i


def insert_tags_1_0_11(source, version):

    # redberry version を 1.0.12 以降と同じ記述にする
    if source.find('{--redberry-converter-version:') == -1:
        # 2行目に
        doctype = '<!DOCTYPE html>'
        i = source.find(doctype)
        if i == -1:
            raise
        i += len(doctype)
        ver_str = '.'.join(map(str, version))
        source = source[:i] + '\n<!-- {{##}}{{--redberry-converter-version:{}--}}{{##}} -->'.format(ver_str) + source[i:]

    # touch.js 追加
    if source.find('touch.js') == -1:
        i = source.find('<body>')
        if i == -1:
            raise
        source = source[:i] + '''
<!-- --{##}>
<script src="http://aimg-pf.gree.net/js/app/touch.js" defer="defer"></script>
<!-- -->
''' + source[i:]

    # script[src] に {{materials_base_path}}/追加
    def repl(m):
        proto = m.group(2)[:4]
        if proto == 'http' or proto[:2] == '{{':
            return m.group(0)
        return '''
<!-- {{% if materials_base_path %}} --{{##}}>
<script{1}src="{{{{materials_base_path}}}}/{2}"{3}></script>
<!-- {{% else %}} -->
{0}
<!-- {{% endif %}} -->
'''.format(m.group(0), m.group(1), m.group(2), m.group(3))
    if source.find('materials_base_path') == -1 or \
        source.find('material_base_path') == -1:
      source = re.sub(
        r'<script([^>]+)src="([^"]+)"([^>]*)></script>',
        repl, source)

    # animation_html_extension差し込むための記述を追加
    if source.find('animation_html_extension') == -1:
        i = source.find('</body>')
        if i == -1:
            raise
        source = source[:i] + '''
<!-- {% if animation_html_extension %}--{##}>{% include animation_html_extension %}<!{##}--{% endif %} -->
''' + source[i:]

    return source

def insert_tags_1_0_12(source, version):

    # 1.0.12 ~ 1.0.13 だとコメントタグが片方しか無いので、正規化
    if source.find('{##}{--redberry-converter-version:') == -1:
        ver_str = '.'.join(map(str, version))
        source = re.sub(
            r'<!--[^>]+{--redberry-converter-version:[\d\.]+--}[^>]+-->',
            '<!-- {{##}}{{--redberry-converter-version:{}--}}{{##}} -->'
            .format(ver_str), source)

    # 1.0.12 ~ 1.0.13 だとextensionの位置が 設定スクリプトより前なので後ろに移動
    ext_tag = '<!-- {% if animation_html_extension %}--{##}>{% include animation_html_extension %}<!{##}--{% endif %} -->'
    i = source.find(ext_tag)
    if i == -1:
        raise
    i += len(ext_tag)
    j = source.find('if animation_html_footer')
    if j == -1:
        raise
    test_str = source[i:j] # だいたい extension ~ footer 間の文字列

    if test_str.find('<script') > -1:
        # scriptタグが入ってたらfooter直前に移動する
        source = source.replace(ext_tag, '')
        i = source.find('include animation_html_footer')
        if i == -1:
            raise
        close_script = '</script>'
        i = source.rfind(close_script, 0, i)
        if i == -1:
            raise
        i += len(close_script)
        source = source[:i] + '\n' + ext_tag + source[i:]

    # 1.0.12 ~ 1.0.14 だと materials_base_path が material_base_path になってるので置換
    source = source.replace('material_base_path', 'materials_base_path')

    return source




