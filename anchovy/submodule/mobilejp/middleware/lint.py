# -*- coding: utf-8 -*-
from lxml import etree

from django.http import HttpResponse
from django.conf import settings
from django.utils.html import escape

XHTML_TYPES = ('text/html', 'application/xml+xhtml')

class XHTMLLintMiddleware(object):
    def process_response(self, request, response):
        if not settings.DEBUG:
            return response

        content_type = response['Content-Type'].split(';')[0]
        if content_type not in XHTML_TYPES:
            return response

        try:
            etree.fromstring(response.content)
            return response
        except etree.Error, e:
            try:
                line, column = e.position
                lines = response.content.splitlines()
                error_html = '\n'.join(lines[line - 5:line + 5])
                return HttpResponse('<html><head></head><body>%s<br /><pre>%s</pre></body></html>' % (e, escape(error_html)))
            except AttribteError:
                return HttpResponse('<html><head></head><body>%s</body></html>' % e)
