# -*- coding: utf-8 -*-
"""
Activity API GREE用

Activity APi for Gree.
"""
from base import ActivityBase
from django.utils.encoding import smart_str


class ActivityGree(ActivityBase):
    """
    Activity APIを使う（GREE用）
    
    Use Activity Api from Gree.
    """

    def send(self, userid, title, url=None):
        """
        アクティビティを送る
        アクティビティは、GREEの「アプリの更新」に表示される
        userid : ユーザID
        title : アクティビティに表示したい文字列
        url : titleのリンク先
        
        Send the activity of the user.
        This information will be dislpayed at screen of Gree with caption 「アプリの更新」 or "renew of application".
        userid: the id of the user
        title: the sentences you want to display at the screen.
        url: the link of title
        
        """
        data = {"title" : smart_str(title, 'utf-8')}
        if url:
            data["url"] = url
        self._request(userid, title, data)

