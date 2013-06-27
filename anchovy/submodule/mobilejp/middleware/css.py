# -*- coding: utf-8 -*-

from django.conf import settings
from mobilejp.css.cssinclude import CssInclude
from mobilejp.log import logger
import datetime

class CssIncludeMiddleware(object):

    def process_response(self, request, response):

        if not request.path.startswith("/m/"):
            return response

        d = datetime.datetime.now()
        
        content_type = response.get('Content-Type',"")
        if ((not content_type.startswith('text/html') and
             not content_type.startswith('application/xhtml+xml')) or
            response.status_code != 200):
            return response
        
        content = response.content
        
        if not content:
            return response

        device = request.device
        if device.is_nonmobile():
            return response

        c = CssInclude()
        
        if device.is_docomo():
            c.setAgentDocomo()
        elif device.is_softbank():
            c.setAgentSoftBank()
        elif device.is_ezweb():
            c.setAgentAu()

        if request.device.display.is_vga():
            c.setVga()
                    
        content = c.apply(content)
        
        response.content = content

        dd = datetime.datetime.now()
        r = dd - d
        logger.debug('(%s/%s)' % (r.seconds, r.microseconds))

        return response

