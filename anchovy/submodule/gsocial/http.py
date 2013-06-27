# -*- coding:utf-8 -*-

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.sites.models import Site

from gsocial.set_container import containerdata
from mobilejp.middleware.mobile import get_is_webview

from setting import GREE

import datetime, time
import urllib
from gsocial.log import Log

class HttpResponseNotAuthorized(HttpResponse):
    """
    HttpResponseNotAuthorized
    """
    status_code = 401

    def __init__(self, redirect_to):
        """
        __init__
        """
        HttpResponse.__init__(self)
        str_authenticate = 'Basic realm="%s"' % Site.objects.get_current().name
        self['WWW-Authenticate'] =  str_authenticate

def HttpResponseOpensocialRedirect(url, request=None):
    """
    If you want to redirect the user`s page to "ordinal HTML page",use this.
    *If user is using smartphone,will set sesssion ID on the initial redirect page with handing the request.
      
    通常のHTMLを返すページにリダイレクトしたい場合はこちらを使う
    ※スマートフォン版で最初に遷移するページの場合、requestを渡して、セッションIDを埋め込む
    """
    if settings.OPENSOCIAL_DEBUG or settings.OPENSOCIAL_CONTAINER.endswith(GREE):
        if request is not None and request.device.is_smartphone and hasattr(request, 'session_id') and not settings.OPENSOCIAL_DEBUG:
            url = 'http://%s%s?%s=%s' % (settings.SITE_DOMAIN, url, settings.SESSION_URL_KEY_NAME, request.session_id)
        else:
            url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
    else:
        app_url = containerdata['app_url'] % {"app_id":settings.APP_ID}
        url += urllib.quote('?signed=1&guid=ON&t=' + str(time.mktime(datetime.datetime.now().timetuple())))
        url = '%s?guid=ON&url=http://%s%s' % (app_url, settings.SITE_DOMAIN, url)
    #requstサービス対策
    #requst判別キーを付与する
    import re
    if request:
        request_key = request.GET.get(settings.GREE_REQUEST_KEY_NAME, None)
        if settings.GREE_REQUEST_API and request_key:
            if re.search('\?', url):
                url += '&%s=%s' % (settings.GREE_REQUEST_KEY_NAME, request_key) 
            else:
                url += '?%s=%s' % (settings.GREE_REQUEST_KEY_NAME, request_key) 

    Log.debug("==================================")
    Log.debug("redirect to: " + url)
    Log.debug("==================================")
    return HttpResponseRedirect(url)

def HttpResponseOpensocialMediaRedirect(url, request=None):
    """
    If you want to redireft the user`s page to "SWF or JPEG",use this.
    *If user is using smartphone,will set sesssion ID on the initial redirect page with handing the request.
    
    SWFやJpegなどへリダイレクトさせたい場合はこちらを使う
    ※スマートフォン版で最初に遷移するページの場合、requestを渡して、セッションIDを埋め込む
    """
    if settings.OPENSOCIAL_DEBUG or settings.OPENSOCIAL_CONTAINER.endswith(GREE):
        if request is not None and request.device.is_nonmobile() and hasattr(request, 'session_id') and not settings.OPENSOCIAL_DEBUG:
            url = 'http://%s%s?%s=%s' % (settings.SITE_DOMAIN, url, settings.SESSION_URL_KEY_NAME, request.session_id)
        else:
            url = 'http://%s%s' % (settings.SITE_DOMAIN, url)
    else:
        media_url = containerdata['media_url'] % {"app_id":settings.APP_ID}
        url += urllib.quote('?signed=1&guid=ON&t=' + str(time.mktime(datetime.datetime.now().timetuple())))
        url = '%s?guid=ON&url=http://%s%s' % (media_url, settings.SITE_DOMAIN, url)
    Log.debug("redirect to: " + url)
    return HttpResponseRedirect(url)
    
