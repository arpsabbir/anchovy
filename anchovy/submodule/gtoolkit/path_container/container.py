# -*- coding:utf-8 -*-
import msgpack
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_unicode
from django.utils.functional import cached_property


class PathContainer(object):
    """
    Path情報を格納するためのクラス
    """

    # デフォルトの保持時間
    DEFAULT_EXPIRE = 60 * 5
    # 削除時のラグ
    DEFAULT_TMP_EXPIRE = 20

    @classmethod
    def get(cls, player_id, container_key, delete=True):
        u""" 格納データを取得
        :param player_id: プレイヤーID
        :param container_key: パスの格納キー
        :param delete: 取得時に削除するかどうか
        :return:
        """
        container = cls(player_id, container_key)
        result = container.load(delete=delete)
        return container if result else None

    def __init__(self, player_id, container_key):
        """
        :param player_id: プレイヤーID
        :type player_id: string

        :param container_key: パスの格納キー
        :type container_key: string or list
        """
        self._player_id = smart_unicode(player_id)
        self._data = None

        if isinstance(container_key, basestring):
            self._container_key = [smart_unicode(container_key)]
        elif isinstance(container_key, list):
            self._container_key = container_key

    def __getattr__(self, item):
        return self._data.get(item)

    @property
    def path(self):
        return self.get_path()

    @property
    def message(self):
        return smart_unicode(self._message)

    def set(self, url_name, url_args=None, message='', expire=None):
        """
        Path情報をpackして格納

        :param url_name: reverse()の第一引数
        :type url_name: string

        :param url_args: reverse()のargs
        :type url_args: list

        :param message: リンク文字列などを渡したい場合に
        :type message: string

        :param expire: データ保持時間 デフォルト5分
        :type expire: int
        """
        self._data = {
            'url_name': url_name,
            'url_args': url_args if url_args else [],
            '_message': message,
        }
        return self.save(expire)

    def save(self, expire=None):
        return cache.set(self._key, msgpack.packb(self._data),
                         expire if expire else self.DEFAULT_EXPIRE)

    def load(self, delete=True, expire=None):
        """
        cacheからデータ取得してunpack

        :param delete: 削除するかどうか
        :type delete: bool

        :param expire: 削除時に実際に削除されるまでのラグ
        :type expire: int

        :return: {'url_name':string, 'url_args':list}
        :rtype: dict or None
        """
        data = cache.get(self._key)
        if data:
            # データが存在したのでunpack
            self._data = msgpack.unpackb(data)

            if delete:
                # 取得されたら20秒後消える
                self.expire(expire if expire else self.DEFAULT_TMP_EXPIRE)

        return self._data if getattr(self, '_data', None) else None

    def delete(self):
        """
        削除する
        """
        return cache.delete(self._key)

    def expire(self, second):
        """
        expireを更新する

        :param second: 更新するexpire
        :type second: int
        """
        return cache.set(self._key, cache.get(self._key), second)

    def get_path(self):
        """
        保存されたパスを返す

        :rtype: string or None
        """
        data = self.load()
        if not data:
            return None

        result = reverse(data['url_name'], args=data['url_args'])

        return result

    @cached_property
    def _key(self):
        return self._make_key()

    def _make_key(self):
        values = [self._player_id]
        values.extend(self._container_key)
        return u':'.join(values)
