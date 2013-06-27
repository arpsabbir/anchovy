# -*- encoding: utf-8 -*-
from django import template
from django.core.urlresolvers import reverse

from gsocial.templatetags.osmobile import (opensocial_session_url_convert,
                                           opensocial_url_convert)
from mobilejp.middleware.mobile import get_current_device, get_current_request

register = template.Library()


@register.tag
def pager(parser, token):
    u"""
    汎用ページネーションを出す

    使い方::

        {% pager <ページネータ> <ビューURL名> [URL引数] %}

    例::

        {% pager pager 'root_index' args1 '#PAGE#' args3 %}
    """
    try:
        args = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "pager tag requires more than 2 argument")

    return PagerNode(args[1], args[2], args[3:])


class PagerNode(template.Node):
    """
    --- Usage ---
    {% pager pager 'root_index' args1 '#PAGE#' args3 %}
    """
    template_name = 'common/parts/pager.html'

    def __init__(self, pager, url_name, url_args):
        self.pager = template.Variable(pager)
        self.url_name = template.Variable(url_name)
        self.url_args = [template.Variable(url_arg) for url_arg in url_args]

    def render(self, context):
        pager = self.pager.resolve(context)
        url_name = self.url_name.resolve(context)
        url_args = [url_arg.resolve(context) for url_arg in self.url_args]

        next_index = pager['current'].next_page_number() \
            if pager['current'].has_next() else None
        prev_index = pager['current'].previous_page_number() \
            if pager['current'].has_previous() else None
        try:
            replace_index = url_args.index('#PAGE#')
        except ValueError:
            replace_index = len(url_args)
            url_args.append('#PAGE#')

        pages = []
        next_url = None
        prev_url = None
        for index in pager['navigator']:
            url_args[replace_index] = index

            # URL生成
            device = get_current_device()
            request = get_current_request()
            reversed_url = reverse(url_name, args=url_args)
            if request and not device.is_featurephone:
                url = opensocial_session_url_convert(reversed_url, request)
            else:
                url = opensocial_url_convert(reversed_url)

            pages.append({
                'index': index,
                'url': url,
            })
            if next_index == index:
                next_url = url
            elif prev_index == index:
                prev_url = url

        pager_context = template.Context({
            'pager': pager,
            'pages': pages,
            'current_index': pager['current'].number,
            'next_url': next_url,
            'next_index': next_index,
            'prev_url': prev_url,
            'prev_index': prev_index,
        })

        pager_template = template.loader.get_template(self.template_name)
        rendered_html = pager_template.render(pager_context)

        return rendered_html
