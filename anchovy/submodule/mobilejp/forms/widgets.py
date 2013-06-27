# -*- coding: utf-8 -*-
import re
from itertools import chain

from django.forms.widgets import *
from django.forms.widgets import Input, RadioInput, RadioFieldRenderer
from django.forms.util import flatatt
from django.utils.html import escape, conditional_escape
from django.utils.encoding import smart_unicode, force_unicode
from django.utils.safestring import mark_safe
from django.utils import datetime_safe

from mobilejp.middleware.mobile import get_current_device

def switch_istyle(carrier, name):
    if carrier == 'N':
        return (None, None)
    elif carrier == 'S':
        return (u'mode', name)
    elif carrier == 'E' or carrier == 'W':
        value = { 'hiragana'   : u"1",
                  'hankakukana': u"2",
                  'alphabet'   : u"3",
                  'numeric'    : u"4" }.get(name, u"1")
        return (u'istyle', value)
    else:
        value = { 'hiragana'   : u"-wap-input-format:'*<ja:h>'",
                  'hankakukana': u"-wap-input-format:'*<ja:hk>'",
                  'alphabet'   : u"-wap-input-format:'*<ja:en>'",
                  'numeric'    : u"-wap-input-format:'*<ja:n>'"
                  }.get(name)
        if value:
            return (u'style', value)
        else:
            return (None, None)


class MobileInput(Input):
    input_type = 'text'

    def __init__(self, attrs=None, istyle=None):
        super(MobileInput, self).__init__(attrs)
        self.istyle = istyle

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        if self.istyle:
            dev = get_current_device()
            if dev is None:
                short_carrier = 'D'
            else:
                short_carrier = dev.short_carrier

            istyle_key, istyle_value = switch_istyle(short_carrier,
                                                     self.istyle)
            if istyle_key:
                attrs[istyle_key] = istyle_value

        final_attrs = self.build_attrs(attrs,
                                       type=self.input_type,
                                       name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return mark_safe(u'<input%s />' % flatatt(final_attrs))


class MobileTextarea(Widget):
    def __init__(self, attrs=None, istyle=None):
        self.istyle = istyle
        self.attrs = {u'cols': u'25', u'rows': u'3'}
        if attrs:
            self.attrs.update(attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''

        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)

        dev = get_current_device()
        istyle_key, istyle_value = switch_istyle(dev.short_carrier, self.istyle)
        if istyle_key:
            final_attrs[istyle_key] = istyle_value
        return mark_safe(u'<textarea%s>%s</textarea>' % (flatatt(final_attrs), escape(value)))

class MobileSelect(Select):
    def render(self, name, value, attrs=None, choices=()):
        """
        Override
        """
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        size = final_attrs.pop('fontsize', 1)
        dev = get_current_device()
        if size and (dev.is_ezweb() or dev.is_nonmobile()):
            format = u'<option value="%%s"%%s><font size="%s">%%s</font></option>' % size
        else:
            format = u'<option value="%s"%s>%s</option>'

        output = [u'<select%s>' % flatatt(final_attrs)]
        str_value = smart_unicode(value) # Normalize to string.
        for option_value, option_label in chain(self.choices, choices):
            option_value = smart_unicode(option_value)
            selected_html = (option_value == str_value) and u' selected="selected"' or ''
            output.append(format % (escape(option_value), selected_html, escape(smart_unicode(option_label))))
        output.append(u'</select>')
        return mark_safe(u''.join(output))


class MobileCheckboxSelectMultiple(CheckboxSelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None:
            value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_unicode(option_value)
            rendered_cb = cb.render(name, option_value)
            output.append(u'%s%s<br />' % (rendered_cb,
                    conditional_escape(force_unicode(option_label))))
        return mark_safe(u''.join(output))

class MobileDateInput(Input):
    input_type = 'text'
    format = '%Y%m%d'

    def __init__(self, attrs=None, format=None):
        super(MobileDateInput, self).__init__(attrs)
        if format:
            self.format = format

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        elif hasattr(value, 'strftime'):
            value = datetime_safe.new_date(value)
            value = value.strftime(self.format)

        if attrs is None:
            attrs = {}

        dev = get_current_device()
        istyle_key, istyle_value = switch_istyle(dev.short_carrier, 'numeric')
        if istyle_key and istyle_value:
            attrs[istyle_key] = istyle_value

        return super(MobileDateInput, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        return u'%s-%s-%s' % (value[0:4], value[4:6], value[6:8])


class NoLabelRadioInput(RadioInput):
    def __unicode__(self):
        return u'%s%s' % (self.tag(), self.choice_label)

class FlatRadioFieldRenderer(RadioFieldRenderer):
    def __unicode__(self):
        "Outputs a <ul> for this set of radio fields."
        buf = []
        for i, choice in enumerate(self.choices):
            buf.append(unicode(NoLabelRadioInput(self.name, self.value, self.attrs.copy(), choice, i)))
        return u''.join(buf)

class FlatRadioSelect(RadioSelect):
    def render(self, name, value, attrs=None, choices=()):
        "Returns a RadioFieldRenderer instance rather than a Unicode string."
        from itertools import chain
        from django.utils.encoding import smart_unicode
        if value is None: value = ''
        str_value = smart_unicode(value) # Normalize to string.
        final_attrs = self.build_attrs(attrs)
        return mark_safe(unicode(FlatRadioFieldRenderer(name, str_value, final_attrs, list(chain(self.choices, choices)))))
