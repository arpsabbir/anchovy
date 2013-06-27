# -*- coding: utf-8 -*-
"""
Request API
全プラットフォーム共通のメソッドを定義している
"""
from gsocial.set_container import Container

class RequestBase(object):
    '''
    Request APIの基礎クラス
    '''
    def __init__(self, request):
        # OpenSocialのContainerを作成する
        self.container = Container(request)

    def create_request_data(self, rawdata=False):
        """
        実際のリクエスト処理を行う
        返り値は辞書である
        """
        return None


