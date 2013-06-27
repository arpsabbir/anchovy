# -*- coding:utf-8 -*-
from time import sleep
from unittest import TestCase
from gtoolkit import path_container

player0 = u'2222'
player1 = u'3333'

path_container.PathContainer.DEFAULT_TMP_EXPIRE = 1


class PathContainerTest(TestCase):
    CONTAINER_KEYS = ['item_use', 'raid_battle']

    # 正しい組み合わせ
    SAMPLE_URLS = {
        'home': {
            'url_name': 'root_home',
            'url_args': None,
            'result_path': '/m/home/',
        },
        'index': {
            'url_name': 'root_index',
            'url_args': None,
            'result_path': '/m/',
        },
    }

    def _path_container_set(self, player_id, container_number, url, **kwargs):
        return path_container.set(
            player_id,
            self.CONTAINER_KEYS[container_number],
            self.SAMPLE_URLS[url]['url_name'],
            url_args=self.SAMPLE_URLS[url]['url_args'],
            **kwargs
        )

    def _path_container_get(self, player_id, container_number, *args, **kwargs):
        return path_container.get(
            player_id,
            self.CONTAINER_KEYS[container_number],
            *args,
            **kwargs
        )

    def _path_container_delete(self, player_id, container_number):
        return path_container.delete(
            player_id,
            self.CONTAINER_KEYS[container_number]
        )

    def test_set(self):
        # セットできる
        self.assertIsNone(self._path_container_set(player0, 0, 'home'),
                          msg=u'setがNone以外を返しています')
        self.assertIsNone(self._path_container_set(player0, 1, 'index'),
                          msg=u'setがNone以外を返しています')
        self._path_container_delete(player0, 0)
        self._path_container_delete(player0, 1)

    def test_get(self):
        # セットしたら取得できる
        self._path_container_set(player0, 0, 'home', message='lorem')
        self.assertEqual(
            self._path_container_get(player0, 0).path,
            self.SAMPLE_URLS['home']['result_path'],
            msg=u'setしたパスが正しく取得できていません'
        )
        self.assertEqual(
            self._path_container_get(player0, 0).message,
            'lorem',
            msg=u'setしたメッセージが正しく取得できていません'
        )

        # 一回取得したらすぐには消えないが数秒後消える
        self.assertEqual(
            self._path_container_get(player0, 0).path,
            self.SAMPLE_URLS['home']['result_path'],
            msg=u'取得時に即削除されてしまっています'
        )
        sleep(1)
        self.assertIsNone(
            self._path_container_get(player0, 0),
            msg=u'取得時に自動削除されていません'
        )

        # 消さずに取得できる
        self._path_container_set(player0, 0, 'home', message=u'あいうえお')
        result = self._path_container_get(player0, 0, delete=False)
        self.assertEqual(
            result.path,
            self.SAMPLE_URLS['home']['result_path'],
            msg=u'setしたパスが正しく取得できていません')
        self.assertEqual(
            result.message,
            u'あいうえお',
            msg=u'setしたメッセージが正しく取得できていません')
        sleep(1)
        self.assertEqual(
            result.path,
            self.SAMPLE_URLS['home']['result_path'],
            msg=u'get時にdelete=Falseなのに正しく取得できていません')
        self._path_container_delete(player0, 0)

        # container keyが違えば別保存
        self._path_container_set(player0, 0, 'home')
        self._path_container_set(player0, 1, 'index')
        result0_0 = self._path_container_get(player0, 0, delete=False)
        result0_1 = self._path_container_get(player0, 1, delete=False)
        self.assertEqual(result0_0.path,
                         self.SAMPLE_URLS['home']['result_path'],
                         msg=u'setしたパスが正しく取得できていません')
        self.assertEqual(result0_0.message,
                         '',
                         msg=u'setしていないはずのメッセージが取得されています')
        self.assertEqual(result0_1.path,
                         self.SAMPLE_URLS['index']['result_path'],
                         msg=u'setしたパスが正しく取得できていません')
        self._path_container_delete(player0, 0)
        self._path_container_delete(player0, 1)

        # PlayerIDが違えば別保存
        self._path_container_set(player0, 0, 'home')
        self._path_container_set(player1, 0, 'index')
        result0_0 = self._path_container_get(player0, 0, delete=False)
        result1_0 = self._path_container_get(player1, 0, delete=False)
        self.assertEqual(result0_0.path,
                         self.SAMPLE_URLS['home']['result_path'],
                         msg=u'setしたパスが正しく取得できていません')
        self.assertEqual(result1_0.path,
                         self.SAMPLE_URLS['index']['result_path'],
                         msg=u'setしたパスが正しく取得できていません')
        self._path_container_delete(player0, 0)
        self._path_container_delete(player0, 1)
        self._path_container_delete(player1, 0)
        self._path_container_delete(player1, 1)

    def test_delete(self):
        # set
        self._path_container_set(player0, 0, 'home')
        self._path_container_set(player0, 1, 'index')
        self._path_container_set(player1, 0, 'index')
        self._path_container_set(player1, 1, 'home')

        # delete
        self._path_container_delete(player0, 0)
        self._path_container_delete(player0, 1)
        self._path_container_delete(player1, 0)
        self._path_container_delete(player1, 1)

        # 確認
        self.assertIsNone(self._path_container_get(player0, 0),
                          msg=u'delete出来ていません')
        self.assertIsNone(self._path_container_get(player0, 1),
                          msg=u'delete出来ていません')
        self.assertIsNone(self._path_container_get(player1, 0),
                          msg=u'delete出来ていません')
        self.assertIsNone(self._path_container_get(player1, 1),
                          msg=u'delete出来ていません')
