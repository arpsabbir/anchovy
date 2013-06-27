# -*- coding: utf-8 -*-
"""
message api base
"""

from gsocial.log import Log
from django.utils.encoding import smart_str
from django.conf import settings
from django.utils import simplejson

from gsocial.utils.announcement.base import PlatformApiBase

class AnnouncementGree(PlatformApiBase):
    """
    Application Announcement API
    https://docs.developer.gree.net/ja/globaltechnicalspecs/api/appannouncementapi

    ag = AnnouncementGree()
    # 新規投稿
    announcement_id = ag.save_announcement('イベント開催中', '塔を登れ!')
    # 編集
    ag.save_announcement('イベント開催中', '塔をよじ登れ!', id=announcement_id)
    # 一覧取得
    ag.get_announcements()
    # 削除
    ag.delete_announcement(announcement_id)
    """

    ENDPOINT_URL = '/announce'
    DEFAULT_DEVICES = ['ios', 'android', 'spweb']
    DEFAULT_IMAGES = []
    DEFAULT_URL = 'http://{}/m/'.format(settings.SITE_DOMAIN)
    DEFAULT_ATTR = {}
    DEFAULT_COUNTRY = ['JP'] #['JP', 'US']

    def save_announcement(self, title, body, id=None, **kwargs):
        """
        アナウンスメントを投稿。
        新規投稿は1アプリごと1時間に1回、編集は1時間に6回
        TODO: start_time Jstを指定できたり、自動解析するように
        :param title: (str) タイトル 255byte
        :param body: (str) 本文 800byte
        :param devices: (str) 配信デバイス ios, android, spweb
        :param images: (list) 画像URLを配列で指定可能。複数指定時はランダム。
                       空の場合は公式ユーザを表示
        :param url: (str) クリックした際の飛び先のURL
        :param attr: (dict) URLに引数として設定するkey,valを連想配列で指定
        :param country: (list) 配信国の指定が可能。現状32ヶ国のみに対応
        :param start_datetime_utc: (str) 配信時間の予約。指定がなければ投稿時の時間。
                          設定された時間から30日後に自動でexpireされる
                          YYYY-mm-dd H:i:s (UTC)
        :return: 登録ID
        """
        if id:
            self._overwrite(id=id, title=title, body=body, **kwargs)
            return id #インターフェイスを揃えるためIDを返すことにする
        else:
            return self._write_new(title=title, body=body, **kwargs)

    def delete_announcement(self, id):
        """
        :param id: アナウンスメントID
        :return: 成功時は空文字。
        :raises: IDが登録されていないなど、失敗したら
                 HTTPError: HTTP Error 503: Service Unavailable
        """
        data_dict = {
            'id': id,
            }
        return self.delete(self.ENDPOINT_URL, data_dict=data_dict)

    def get_announcements(self):
        """
        登録してあるアナウンスメント一覧をリストで返す
        [
            {
                "id":"201210_85",
                "app_id":"15746",
                "messages":{
                    "ja-Jpan-JP":{
                        "title":"?\\u5e25?\\u3083???",
                        "body":"\\u832f??"
                        }
                    },
                "devices":["ios","android"],
                "images":["http:\\/\\/example.com\\/sample.png"],
                "url":"http:\\/\\/example.com",
                "attr":{"key1":"val1","key2":"val2","key3":"val3"},
                "country":["JP","US"],
                "start_time":"2012-10-13 05:35:04",
                "end_time":"2012-11-12 05:35:04"
            },
            ...
        ]
        """
        result_json = self.get(self.ENDPOINT_URL)
        parsed = simplejson.loads(result_json)
        if parsed:
            return parsed.get('entry', [])
        return parsed # おそらく空リスト

    def _create_data_dict(self, **kwargs):
        """
        POSTデータ(json)の元になるdictを作成
        """
        title = kwargs['title']
        body = kwargs['body']
        if kwargs.get('force_str', False):
            title = smart_str(title)
            body = smart_str(body)
        start_time = None
        if kwargs.get('start_datetime_utc', False):
            start_time = kwargs['start_datetime_utc'].strftime('%Y-%m-%d %H:%M:%S')
        data_dict = {
            'messages': {
                'ja-Jpan-JP': {
                    'title': title,
                    'body': body,
                }
            },
            'devices': kwargs.get('devices', self.DEFAULT_DEVICES),
            'images': kwargs.get('images', self.DEFAULT_IMAGES),
            'url': kwargs.get('url', self.DEFAULT_URL),
            'attr': kwargs.get('attr', self.DEFAULT_ATTR),
            'country': kwargs.get('country', self.DEFAULT_COUNTRY),
            'start_time': start_time,
        }
        if 'id' in kwargs:
            data_dict['id'] = kwargs['id']
        return data_dict

    def _write_new(self, title, body, **kwargs):
        """
        新規保存。保存したidを返す
        """
        data_dict = self._create_data_dict(title=title, body=body, **kwargs)
        result = self.post(self.ENDPOINT_URL, data_dict=data_dict)
        return self._get_id_from_result(result)

    def _get_id_from_result(self, result_json):
        """
        保存結果jsonから登録IDを取得
        """
        if result_json:
            try:
                result_dict = simplejson.loads(result_json)
            except simplejson.JSONDecodeError, e:
                Log.warn(e)
                return None
            else:
                return result_dict['entry'][0]['id']

    def _overwrite(self, title, body, id=None, **kwargs):
        """
        上書き。
        :return: 空文字固定
        """
        data_dict = self._create_data_dict(id=id, title=title, body=body, **kwargs)
        return self.put(self.ENDPOINT_URL, data_dict=data_dict)

