# -*- coding: utf-8 -*-
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.utils.cache import cc_delim_re
from django.contrib.sessions.backends.base import SessionBase

TEST_COOKIE_NAME = SessionBase.TEST_COOKIE_NAME
TEST_COOKIE_VALUE = SessionBase.TEST_COOKIE_VALUE

from mobilejp.utils.session import embed_session_id, parse_session_id, session_uri

class PseudoCookieMiddleware(object):
    def process_request(self, request):
        try:
            device = request.device
        except AttributeError, e:
            raise e

        # Force to rewrite path and path_info
        # to strip session ID embedded in URL
        newpath, session_id = parse_session_id(request.path)
        request.path = newpath
        request.path_info = newpath

        # If no session ID in URL found,
        # we don't have to touch COOKIE
        if session_id is None:
            return

        # If the client supports cookie or is crawler,
        # then we shouldn't use session ID in URL.
        # Tell her right URL
        if device.supports_cookie() or device.is_crawler():
            return HttpResponsePermanentRedirect(newpath)

        # Use session_id only when the device doen't support cookie.
        # In other case, don't touch the session ID and use original one.
        request.COOKIES[settings.SESSION_COOKIE_NAME] = session_id
        request.COOKIES[TEST_COOKIE_NAME] = TEST_COOKIE_VALUE

    def process_response(self, request, response):
        try:
            device = request.device
        except AttributeError, e:
            raise e

        if device.supports_cookie() or device.is_crawler():
            return response

        try:
            session_key = request.session.session_key
        except AttributeError:
            try:
                session_key = response.cookies[settings.SESSION_COOKIE_NAME]
            except KeyError:
                session_key = None

        if session_key is None:
            return response

        # Remove outgoing session cookie
        try:
            del response.cookies[settings.SESSION_COOKIE_NAME]
        except KeyError:
            pass

        # Strip "Vary: Coookie" header
        try:
            vary_headers = [x for x in cc_delim_re.split(response['Vary']) if x.lower() != 'cookie']
            if vary_headers:
                response['Vary'] = ', '.join([x for x in vary_headers])
            else:
                del response['Vary']
        except KeyError:
            pass

        if isinstance(response, HttpResponseRedirect):
            location = embed_session_id(response['Location'],
                                        session_key,
                                        domain=request.get_host())
            response = HttpResponseRedirect(location)
            return response

        response.content = session_uri(response.content,
                                       session_key,
                                       domain=request.get_host(),
                                       base=request.path)
        return response
