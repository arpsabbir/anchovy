# -*- coding: utf-8 -*-
"""
Activity API
全プラットフォーム共通のメソッドを定義している

Activity API
Define the method which will be commonly used in every platform API.
"""
from gsocial.set_container import Container
from django.utils import simplejson


class ActivityBase(object):
    """
    Activity APIの基底クラス
    
    Base Class of ActivityAPI
    """

    def __init__(self, request=None):
        # gsocialのContainerを生成する
        self.container = Container(request)

    def _request(self, userid, title, data):
        """
        OAuth リクエスト
        Oauth request
        """
        json = simplejson.dumps(data, ensure_ascii=False)
        header_params = {'Content-Type': 'application/json'}
        self.container.oauth_request('POST',
                                     userid,
                                     '/activities/@me/@self/@app',
                                     data=json,
                                     headers=header_params,
                                     )

    def send(self, userid, title, url=None, mobile_url=None, media=None):
        """
        アクティビティを送る
        Send Activity
        """
        return None
