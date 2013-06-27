# -*- coding: utf-8 -*-
"""
message api base
"""
from gsocial.set_container import Container
#from django.conf import settings
#import threading
#import time
#from gsocial.log import Log


class MessageBase(object):
    '''
    Message APIを使う(基礎）
    '''

    def __init__(self, request=None):
        # OpenSocialのContainerを生成する
        self.container = Container(request)
    
    def _api_request(self, sender_osuser_id, path, data):
        '''
        OAuth リクエスト
        '''
        return None

