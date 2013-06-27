# -*- coding: utf-8 -*-
"""
共通機能。1階層上に置きたい
"""
from django.utils import simplejson

from gsocial.set_container import Container

class PlatformApiBase(object):
    """
    プラットフォームへのリクエスト送信のベース
    """

    def __init__(self, request=None):
        # OpenSocialのContainerを生成する
        self.container = Container(request)

    def platform(self):
        """
        return platform
        """
        return 'gree'

    def get(self, path, params=None, sender_osuser_id=None):
        """
        HTTP Get
        """
        return self.container.oauth_request(
            'GET', sender_osuser_id, path, params=params)

    def delete(self, path, data_dict=None, sender_osuser_id=None):
        """
        HTTP Delete
        """
        return self._request('DELETE', path, data_dict, sender_osuser_id)

    def post(self, path, data_dict=None, sender_osuser_id=None):
        """
        HTTP Post
        """
        return self._request('POST', path, data_dict, sender_osuser_id)

    def put(self, path, data_dict=None, sender_osuser_id=None):
        """
        HTTP Put
        """
        return self._request('PUT', path, data_dict, sender_osuser_id)

    def _request(self, method, path, data_dict, sender_osuser_id):
        """
        :param method: GET, POST, PUT, DELETE
        :param path: Endpoint path
        :param data_dict: POST data
        :param sender_osuser_id:
        :return:
        """
        if data_dict:
            # Jsonリクエスト
            data_json = simplejson.dumps(data_dict, ensure_ascii=True)
            headers = {'Content-Type': 'application/json; charset=utf8'}
            return self.container.oauth_request(method, sender_osuser_id, path,
                data=data_json, headers=headers, body_hash=True)
        else:
            return self.container.oauth_request(method, sender_osuser_id, path,
                body_hash=False)
