# -*- coding:utf-8 -*-
import re
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.template.loaders.filesystem import Loader as FileSystemLoader


SCRIPT_SRC = re.compile(
    r'<script\s+type="text/javascript"\s+src="([^"]+)"\s*></script>')
CENTERING_JUDGE = re.compile(r'\(rb_get_enable_centering(\(\))?\)')


def is_animation_template(path):
    """
    html5movieなテンプレかどうか
    """
    return path and path.find('static/movies/html') > -1


def append_animation_tags(source, path):
    """
    animation用タグを突っ込む
    """

    # {% extends 'hoge' %}があるファイルは処理しない
    if source.find('{% extends ') > -1:
        return source

    # {% load animation_tags %}を1行目に突っ込む
    if source.find('{% load animation_tags %}') == -1:
        source = '{% load animation_tags %}\n' + source

    # srcに{{ material_base_path }}突っ込む
    def insert_path(m):
        m1 = m.group(1)
        if m1.find('materials_base_path') == -1:
            return '<script type="text/javascript" src="{}{}"></script>'.format(
                '{{ materials_base_path }}/', m1)
        return m.group(0)

    source = SCRIPT_SRC.sub(insert_path, source)

    is_inline = path.find('inline') > -1

    # スクロール処理などを突っ込む
    insertion_source = '{{ child_movie_clip_links|safe }}\n'
    if not is_inline:
        insertion_source += '<style>*{margin:0;padding:0;}:root{background:#000;min-height:600px;}canvas{position:relative !important;display:block !important;margin:0 auto !important;}</style>'
    if not is_inline and source.find('touch.js') == -1:
        insertion_source += '{% if OPENSOCIAL_SANDBOX %}<script src="http://pf-sb.gree.net/js/app/touch.js"></script>{% else %}<script src="http://aimg-pf.gree.net/js/app/touch.js"></script>{% endif %}\n'
    if not is_inline and source.find('GREE.ui(') == -1:
        insertion_source += '<script>window.onload=function(){GREE.ui({"method":"scroll","x": 0,"y": 0});};</script>\n'
    if source.find('write_redberry_configuration_modifier') == -1:
        insertion_source += '<script>{% write_redberry_configuration_modifier %}</script>\n'

    # 拡大処理を強制OFF
    func_str = 'function rb_get_enable_window_scale_ratio'
    i = source.find(func_str)
    if i > -1:
        source = source[:i+len(func_str)] + '__orig' + source[i+len(func_str):]
        insertion_source += '<script>function rb_get_enable_window_scale_ratio(){return false;}</script>\n'

    # センタリング処理を強制OFF
    source = CENTERING_JUDGE.sub('(false)', source)

    # script挿入
    if len(insertion_source) > 0:
        i = source.find('<!-- {--PLACEHOLDER_FOR_EXTERNAL_SCRIPT--} -->')
        if i > -1:
            source = source[:i] + insertion_source + source[i:]
        else:
            #仕方ないので最後に突っ込む
            source += insertion_source

    if not is_inline and settings.DEBUG:
        source += '<div style="width:320px;background:#888;word-break:break-all;margin:20px auto;color:#fff;">{% include "debug/parts/debug_footer.html" %}<a href="{{next_url}}">next_url: {{next_url}}</a></div>'

    return source


class Loader(FileSystemLoader):
    """
    animation html用にdjangoタグ突っ込む
    """
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        if not template_dirs:
            raise TemplateDoesNotExist

        tried = []
        for file_path in self.get_template_sources(template_name,
                                                   template_dirs):

            if not is_animation_template(file_path):
                # アニメーション用でない
                raise TemplateDoesNotExist

            try:
                file_handler = open(file_path)
                try:
                    source = file_handler.read().decode(settings.FILE_CHARSET)
                finally:
                    file_handler.close()

                if source.find('redberry') == -1:
                    # redberryでない
                    raise TemplateDoesNotExist

                # redberry用置き換え
                source = append_animation_tags(source, file_path)
                return source, file_path

            except IOError:
                tried.append(file_path)

        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(error_msg)
    load_template_source.is_usable = True

_loader = Loader()
