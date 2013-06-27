# -*- coding: utf-8 -*-
"""
Blacklist API(Ignorelist API)
全プラットフォーム共通のメソッドを定義している
"""
from gsocial.set_container import Container


class BlacklistBase(object):
    """
    Blacklist API（GREEでは、Ignorelist API）の基底クラス
    """

    RETRY_COUNT = 3

    def __init__(self, request):
        # OpenSocialのContainerを生成する
        self.container = Container(request)

    def get_response(self, userid, path):
        """
        プラットフォームにリクエストし、そのレスポンスを返す
         JSONを返す
         レスポンスコードは返さない
        """
        return self.container.oauth_request('GET', userid, path)

    def blacklist_check(self):
        """
        二者間でのブラックリストチェック
        """
        return None
