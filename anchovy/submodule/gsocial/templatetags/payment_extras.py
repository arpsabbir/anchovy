# -*- coding: utf-8 -*-
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from django.template import TemplateSyntaxError
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def escape_json(text):
    u"""
    Jsonをエスケープするフィルタ

    例:
        <input type="hidden" name="spam" value="{{ param_json|escape_json}}" />
    """
    text = text.replace('\\','\\\\')
    text = text.replace('\r','\\r')
    text = text.replace('\n','\\n')
    text = text.replace('"','\\"')
    return mark_safe(text)
