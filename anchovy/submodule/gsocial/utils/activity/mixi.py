# -*- coding: utf-8 -*-
"""
Activity API MIXI
"""
from base import ActivityBase
from django.utils.encoding import smart_str


class ActivityMixi(ActivityBase):
    """
    ActivityAPI を使う（MIXI用）
    """

    def platform(self):
        """
        プラットフォーム名を返す
        """
        return 'mixi'

    def send(self, userid, title, url=None, mobile_url=None, media=None):
        """
        アクティビティを送る
        userid : ユーザID
        title : アクティビティに表示したい文字列
        url : titleのリンク先
        mobile_url :
        media :
        """
        data = {"title" : smart_str(title, 'utf-8')}
        if url:
            data["url"] = url
        # mixi の場合のみ mobileUrl と mediaItems を指定できる
        if mobile_url:
            data["mobileUrl"] = mobile_url
        if media:
            data["mediaItems"] = media

        self._request(userid, title, data)
