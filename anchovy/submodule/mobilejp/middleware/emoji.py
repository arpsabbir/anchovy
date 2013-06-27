# -*- coding: utf-8 -*-
import re

from django.conf import settings
from django.utils.encoding import smart_str

import mobilejpcodecs
from mobilejp.emoji.compat import to_str
from mobilejp.log import logger


EMOJI_RE = re.compile(ur'([\ue001-\uf0fc])')

def emoji_repl(matcher):
    code = '%x' % ord(matcher.group(1))
    return u'&#x%s;' % code.upper()

class EmojiMiddleware(object):
    def process_request(self, request):
        logger.debug('emoji_request')
        assert hasattr(request, 'device'), "The mobilejp emoji middleware requires User-Agent middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'mobilejp.middleware.mobile.UserAgentMobileMiddleware'."

        device = request.device
        if device.is_ezweb:
            request.encoding = 'x_sjis_kddi'
        elif device.is_softbank:
            request.encoding = 'x_utf8_softbank'
        elif device.is_docomo:
            # docomo, willcom, nonmobile
            request.encoding = 'x_sjis_docomo'

    def process_response(self, request, response):
        logger.debug('emoji_response')
        if not request.device.is_featurephone:
            return response

        try:
            content_type = response['content-type']
        except KeyError:
            return response

        if (not content_type.startswith('text/html') and
            not content_type.startswith('application/xhtml+xml')):
            return response

        if request.device.is_docomo:
            # override content type
            content_type = 'application/xhtml+xml'

        if request.device.is_softbank and request.encoding == 'x_utf8_softbank':
            response._headers['content-type'] = ('Content-Type',
                                             '%s; charset=UTF-8' % content_type.split(";", 1)[0])
        else:
            response._headers['content-type'] = ('Content-Type',
                                             '%s; charset=Shift_JIS' % content_type.split(";", 1)[0])

        charset = request.encoding

        str_content = smart_str(''.join(response._container).strip(), charset, errors='xmlcharrefreplace')
        str_content = to_str(str_content, charset)
        content = str_content.decode(charset)
        
#        print "process_response------0"
#        print content
#        print "process_response------1"
#        if request.device.is_softbank():
#            content = EMOJI_RE.sub(emoji_repl, content)

        response._charset = charset
        response.content = content

        return response
