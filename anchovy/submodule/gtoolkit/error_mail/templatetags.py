# -*- coding: utf-8 -*-

import sys
import traceback
from django.core.handlers.base import BaseHandler
from django.conf import settings
from django.core.mail import mail_admins

from django.utils.encoding import smart_str, smart_unicode
import logging

logger = logging.getLogger('exception')

old_handle_uncaught_exception = BaseHandler.handle_uncaught_exception

def new_handle_uncaught_exception(self, request, resolver, exc_info):
    logging.debug("new_handle_uncaught_exception")
    if is_mail():
        try:
            _mail_admins_exception(request, exc_info)
        except:
            pass
    return old_handle_uncaught_exception(self, request, resolver, exc_info)

BaseHandler.handle_uncaught_exception = new_handle_uncaught_exception


def _mail_admins_exception(request, exc_info):
    """
    例外をADMINSにメール
    django/core/handlers/base.py  147 def handle_uncaught_exception を真似した

    :return:
    :rtype: None
    """
    try: 
        request_repr = repr(request) 
    except: 
        request_repr = "Request repr() unavailable"

    try:
        exception_type = exc_info[0].__name__
    except:
        exception_type = ''

    try:
        exception_message = exc_info[1]
    except:
        exception_message = ''
    
    values = {
        'SANDBOX_SIGN': smart_unicode(_get_sandbox_sign()),
        'SYSTEM_NAME': smart_unicode(_get_system_name()),
        'HOSTNAME': smart_unicode(_get_hostname()),
        'EXCEPTION_TYPE': smart_unicode(exception_type),
        'EXCEPTION_MESSAGE': smart_unicode(exception_message),
        'OSUSERID': smart_unicode(_get_osuser_id(request)),
        'REQUEST_PATH': smart_unicode(request.path),
        'TRACEBACK_LOG': smart_unicode('\n'.join(traceback.format_exception(*sys.exc_info()))),
        'REQUEST_REPR': smart_unicode(request_repr),
    }
    
    try:
        subject = ERROR_MAIL_SUBJECT_TEMPLATE % values
    except UnicodeDecodeError:
        subject = u'subject unavalable(UnicodeDecodeError) %r' % values
    try:
        message = ERROR_MAIL_MESSAGE_TEMPLATE % values
    except UnicodeDecodeError:
        message = u'message unavalable(UnicodeDecodeError)\n%r' % values
    
    mail_admins(subject, message)
    logger.error(values)
    return True


ERROR_MAIL_SUBJECT_TEMPLATE = u"""%(SANDBOX_SIGN)s%(SYSTEM_NAME)s Error.  %(EXCEPTION_TYPE)s in %(REQUEST_PATH)s"""

ERROR_MAIL_MESSAGE_TEMPLATE = u"""\
system_name:
    %(SANDBOX_SIGN)s%(SYSTEM_NAME)s

hostname:
    %(HOSTNAME)s

exception_type:
    %(EXCEPTION_TYPE)s

exception_message:
    %(EXCEPTION_MESSAGE)s

osuser_id:
    %(OSUSERID)s

request_path:
    %(REQUEST_PATH)s

----------------------------------------
%(TRACEBACK_LOG)s
----------------------------------------
%(REQUEST_REPR)s
"""


def _get_sandbox_sign():
    if settings.OPENSOCIAL_SANDBOX:
        return u'[SANDBOX] '
    else:
        return u''


def _get_system_name():
    return getattr(settings, 'APP_NAME', '')


def _get_hostname():
    try:
        import socket
        return socket.gethostbyaddr(socket.gethostname())[0]
    except:
        return ''


def _get_osuser_id(request):
    """
    osuser名
    """
    try:
        return getattr(request, 'opensocial_viewer_id', None) or \
            request.REQUEST.get('opensocial_viewer_id', None) or \
            request.session.get('opensocial_userid', '-')
    except:
        return u"Osuser unavailable."


def is_mail():
    return getattr(settings, 'ERROR_PAGE_MAIL', False)