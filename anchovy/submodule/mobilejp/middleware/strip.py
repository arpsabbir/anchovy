# -*- coding: utf-8 -*-
"""
>>> _strip('<p style="width:100%" > The quick </p>  brown fox  <p>  jumps  </p>')
'<p style="width:100%" >The quick</p>brown fox<p>jumps</p>'
"""

import re
from mobilejp.log import logger

RE_STRIP = re.compile(r'>\s*(.*?)\s*<')


def _strip(content):
    return RE_STRIP.sub(r'>\1<', content)


class StripMiddleware(object):
    def process_response(self, request, response):
        logger.debug("strip_response")

        if not request.path.startswith("/m/"):
            return response

        content_type = response.get('Content-Type', "")
        if ((not content_type.startswith('text/html') and
             not content_type.startswith('application/xhtml+xml')) or
                response.status_code != 200):
            return response

        content = response.content

        if not content:
            return response

        content = _strip(content)

        response.content = content
        return response
