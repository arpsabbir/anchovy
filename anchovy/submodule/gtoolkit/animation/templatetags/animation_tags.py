# -*- coding: utf-8 -*-
from django import template
from django.utils.safestring import mark_safe
from django.utils.encoding import smart_unicode
from ..render import NoQuotingString

register = template.Library()

def _write_args_type_var(key, value):
    if isinstance(value, (int, float, long)):
        return u'var {key} = Number("{value}");'.format(key=key, value=value)
    elif isinstance(value, list):
        return u'var {key} = [{value}];'.format(key=key, value=u','.join([smart_unicode(s) for s in value]))
    elif isinstance(value, (str, unicode)):
        return u'var {key} = "{value}";'.format(key=smart_unicode(key), value=smart_unicode(value))


def _write_args_type_dict_item(key, value):
    if isinstance(value, (int, float, long)):
        return u'{key}: Number("{value}")'.format(key=key, value=value)
    elif isinstance(value, list):
        return u'{key}: [{value}]'.format(key=key, value=u','.join([smart_unicode(s) for s in value]))
    elif isinstance(value, NoQuotingString):
        return u'{key}: {value}'.format(key=smart_unicode(key), value=smart_unicode(value))
    elif isinstance(value, (str, unicode)):
        return u'{key}: "{value}"'.format(key=smart_unicode(key), value=smart_unicode(value))


def _write_params_type_dict_item(params):
    return mark_safe(
        u',\n'.join([param for param in params if param])
    )


def _write_params_type_var(params):
    return mark_safe(
        u'<script type="text/javascript">{params}</script>'.format(
            params=u'\n'.join([param for param in params if param])
        )
    )


def _write_args(context, keys, output_dict=False):
    if output_dict:
        params = [_write_args_type_dict_item(key, context[key]) for key in keys if key in context]
        return _write_params_type_dict_item(params)

    params = [_write_args_type_var(key, context[key]) for key in keys if key in context]
    return _write_params_type_var(params)


@register.simple_tag(takes_context=True)
def write_params(context):
    u"""
    ムービーに基本的な引数をロードする

    必要なパラメータは、テンプレートに渡されたコンテキストデータから持ってくる。
    next_url, next_url2 はデフォルトで取得し、
    param_keys がコンテキストにあれば、その名前のパラメータも埋め込む。

    使い方::

        {% write_params %}
    """
    keys = ['next_url', 'next_url2'] + context['param_keys']
    return _write_args(context, keys)


@register.simple_tag(takes_context=True)
def write_params_redberry(context):
    u"""
    RedBerry用の引数を書き込むコードを出力する

    必要なパラメータは、テンプレートに渡されたコンテキストデータから持ってくる。

    使うコンテキストデータは、next_url, next_url2, param_keys,
    redberry_replace_images, redberry_common_path, redberry_orig_path

    これ以上に詳しい説明はコードを読んでください。

    使い方:

        {% write_params_redberry %}
    """
    return mark_safe(u"""
      var gtoolkit_animation_params = {
        %s
      }
      var gtoolkit_animation_replace_images = {
        %s
      }
      for (var param_key in gtoolkit_animation_params) {
        custom.globals[param_key] = gtoolkit_animation_params[param_key]
      }
      bitmaps_length = custom.bitmaps.length;
      for (var i = 0; i< bitmaps_length; i++) {
        if (gtoolkit_animation_replace_images[custom.bitmaps[i][1]]) {
          custom.bitmaps[i][4] = '%s/' + gtoolkit_animation_replace_images[custom.bitmaps[i][1]]
        } else {
          custom.bitmaps[i][4] = '%s/' + custom.bitmaps[i][4]
        }
      }
""" % (

        _write_args(context,
            ['next_url', 'next_url2'] + context['param_keys'],
            output_dict=True),
        _write_args(context['redberry_replace_images'],
            context['redberry_replace_images'].keys(),
            output_dict=True),
        context['redberry_common_path'],
        context['redberry_orig_path'],
    ))


@register.simple_tag(takes_context=True)
def write_redberry_configuration_modifier(context):
    u"""
    RedBerry用のconfiguration_modifierでパラメータを書き込むコードを出力する

    使うコンテキストデータは、next_url, next_url2, param_keys,
    redberry_replace_images, redberry_common_path, redberry_orig_path

    これ以上に詳しい説明はコードを読んでください。

    使い方:

        {% write_redberry_configuration_modifier %}
    """
    return mark_safe(u"""
    function rb_configuration_modifier(config) {
          var gtoolkit_animation_params = {
            %(animation_params)s
          }
          var gtoolkit_animation_replace_images = {
            %(replace_images)s
          }
          for (var param_key in gtoolkit_animation_params) {
            config.globals[param_key] = gtoolkit_animation_params[param_key]
          }
          bitmaps_length = config.bitmaps.length;
          for (var i = 0; i< bitmaps_length; i++) {
            if (gtoolkit_animation_replace_images[config.bitmaps[i][1]]) {
              config.bitmaps[i][4] = '%(common_path)s/' + gtoolkit_animation_replace_images[config.bitmaps[i][1]]
            } else {
              config.bitmaps[i][4] = '%(orig_path)s/' + config.bitmaps[i][4]
            }
          config.child_movieclips = {
            %(child_movieclips)s
          };
        }
      return config;
    }
""" % {
        'animation_params':
            _write_args(context,
                        ['next_url', 'next_url2'] + context['param_keys'],
                        output_dict=True),
        'replace_images':
            _write_args(context['redberry_replace_images'],
                        context['redberry_replace_images'].keys(),
                        output_dict=True),
        'common_path':
            context['redberry_common_path'],
        'orig_path':
            context['redberry_orig_path'],
        'child_movieclips':
            _write_args(context['redberry_replace_clips'], context['redberry_replace_clips'].keys(),
                        output_dict=True)
            #'"avt": rb_4',
    })


@register.filter
def is_inline(animation_name):
    """
    inlineという文字が含まれるか返す
    """
    return animation_name.find('inline') > -1

