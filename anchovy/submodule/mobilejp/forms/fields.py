# -*- coding: utf-8 -*-
from django.forms import ValidationError
from django.forms.fields import *
from django.forms.fields import EMPTY_VALUES
from django.utils.encoding import smart_unicode

from mobilejp.emoji import quote
from mobilejp.middleware.mobile import get_current_device

class EmojiField(CharField):
    def clean(self, value):
        """
        Validates max_length and min_length. Returns a Unicode object.
        """
        super(CharField, self).clean(value)
        if value in EMPTY_VALUES:
            return u''

        value = smart_unicode(value)
        value_length = len(value)
        if self.max_length is not None and value_length > self.max_length:
            raise ValidationError(self.error_messages['max_length'] % {'max': self.max_length, 'length': value_length})
        if self.min_length is not None and value_length < self.min_length:
            raise ValidationError(self.error_messages['min_length'] % {'min': self.min_length, 'length': value_length})

        device = get_current_device()
        value = quote(value, device.short_carrier)

        return value

