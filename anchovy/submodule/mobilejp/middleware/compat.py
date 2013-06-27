# -*- coding: utf-8 -*-
import re

_ACCESS_KEY_RE = re.compile(r'(?:<a(\W[^>]*\b)accesskey=(?:\'|"|)(\w)(?:\'|"|)([^>]*)>)', re.I)

class VodafoneCompatibilityMiddleware(object):
    def process_response(self, request, response):
        device = request.device
        if device.is_softbank() and not device.is_3g():
            # Fix access key compatibility
            response._container = [_ACCESS_KEY_RE.sub(lambda m: u'<a%sdirectkey="%s" nonumber%s>' % m.groups(),
                                                      value) for value in response._container]

            # Fix mailto scheme compatibility
            # TODO
            # replace 'href="mailto:addr?body=b&subject=s"'
            # to 'href="mailto:addr' mailbody="b"'

        return response
