# -*- coding: utf-8 -*-
"""
Device情報
"""
from mobilejp.log import logger

from uamobile import detect, Context
import re
SMARTPHOPNE_RE = re.compile(r'Android|iPhone|iPad|Windows Phone OS')
IOS_RE = re.compile(r'iPhone|iPad')
ANDROID_RE = re.compile(r'Android')
WINDOWSPHONE_RE = re.compile(r'Windows Phone OS')
WEBVIEW_RE = re.compile(r'GreeWebview|WEBVIEW|webview')

class MobileDevice(object):
    """
    モバイル端末情報
    """
    is_featurephone = False
    is_smartphone = False
    is_pc = False
    is_webview = False
    is_ios = False
    is_android = False
    is_windowsphone = False
    is_docomo = False
    is_au = False
    is_ezweb = False
    is_softbank = False
    version = ''
    name  = ''
    detect = None

    def __init__(self, request, context=None):
        logger.debug("mobilejp __init__ start")
        #logger.debug(request)
        logger.debug("mobilejp __init__ end")
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        web_user_agent = request.REQUEST.get('X-GREE-User-Agent', '')
        self._featurephone_check(request, context)
        self._smartphone_check(user_agent)
        self._pc_check()
        self._webview_check(web_user_agent, request)


    def _featurephone_check(self, request, context):
        """
        uamobileのdetectを使い、featurephone識別をする
        """
        ua_agent = detect(request.META, context)
        self.detect = ua_agent

        if ua_agent.is_docomo():
            self.is_featurephone = True
            self.is_docomo = True
            self.name = 'docomo'
        elif ua_agent.is_ezweb():
            self.is_featurephone = True
            self.is_au = True
            self.is_ezweb = True
            self.name = 'au'
        elif ua_agent.is_softbank():
            self.is_featurephone = True
            self.is_softbank = True
            self.name = 'softbank'

    def _smartphone_check(self, user_agent):
        """
        UserAgent情報からスマートフォン式別などを行う
        """
        if SMARTPHOPNE_RE.search(user_agent):
            self.is_smartphone = True

            if ANDROID_RE.search(user_agent):
                self.is_android = True
                self.name = 'Android'
                version_search = re.search(r'Android (.*?)\;', user_agent)
                if version_search:
                    self.version = version_search.group(1)
            elif IOS_RE.search(user_agent):
                self.is_ios = True
                self.name = 'iOS'
                version_search = re.search(r'OS (.*?) like', user_agent)
                if version_search:
                    self.version = version_search.group(1)
            elif WINDOWSPHONE_RE.search(user_agent):
                self.is_windowsphone = True
                self.name = 'WindowsPhone'
                version_search = re.search(r'Windows Phone OS (.*?)\;', user_agent)
                if version_search:
                    self.version = version_search.group(1)

    def _webview_check(self, user_agent, request):
        """
        UserAgent情報からWebView式別などを行う
        """
        logger.debug("mobilejp _webview_check start")
        logger.debug("mobilejp useragent: %s" % user_agent)
        logger.debug("mobilejp check webview %s" % WEBVIEW_RE.search(user_agent))
        logger.debug("mobilejp check session:: %s" % request.session.get('is_webview'))
        logger.debug("mobilejp check session items:: %s" % request.session.items())
        logger.debug("mobilejp _webview_check end")

        if WEBVIEW_RE.search(user_agent) or request.session.get('is_webview'):
            self.is_webview = True

    def _pc_check(self):
        if self.is_featurephone is False and self.is_smartphone is False:
            self.is_pc = True