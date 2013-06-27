# -*- coding: utf-8 -*-
"""
Activity API MOBAGE
"""
from base import ActivityBase
from django.utils.encoding import smart_str


class ActivityMobage(ActivityBase):
    """
    Activity APIを使う（MOBAGE用）
    """

    def send(self, userid, title, url=None):
        """
        アクティビティを送る
        userid : ユーザID
        title : アクティビティに表示したい文字列
        url : titleのリンク先
        """
        data = {"title" : smart_str(title, 'utf-8')}
        if url:
            data["url"] = url
        self._request(userid, title, data)

