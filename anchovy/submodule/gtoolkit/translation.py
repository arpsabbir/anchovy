# -*- coding: utf-8 -*-
"""
django.utils.translation.ugettext が str を返すので unicode に変換する.

>>> from gtoolkit.translation import ugettext as _
>>> _('spam')
"""
from django.utils.translation import ugettext as django_ugettext
from django.utils.encoding import smart_unicode

def ugettext(message):
    return smart_unicode(django_ugettext(message))
