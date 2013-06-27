# -*- coding:utf-8 -*-
"""

Path Container

一時的にパスを格納する仕組み
イベントで基本機能のアイテム使用画面に遷移させた後イベント画面に戻す時などに使用する

遷移をまたいで使うreverse()のようなイメージ。一度取り出すと消える



例:

from gtoolkit import path_container

# レイドのアイテム使用View
class RaidBattleItemUseView(View):
    def get(self, item_id):
        # 戻り先URLをパスコンテナにセットする
        path_container.set(self.player.id, 'item_use_execute', url_name='e001_raid_battle_execute', url_args=[player_raid_boss.id, use_point])

        # アイテム使用にリダイレクト
        return HttpResponseOpensocialRedirect(reverse('item_use_execute', args=[item_id]))


# アイテム使用
class ItemUseExecuteView(View):
    def get(self, item_id):

        ...(アイテム使用ロジック)

        another_path = path_container.get(self.player.id, 'item_use_execute')
        if another_path:
            # 他へのリダイレクトが指定されていたらそっちへ
            HttpResponseOpensocialRedirect(another_path)

        # 結果画面へ
        return HttpResponseOpensocialRedirect(reverse('item_use_result'))


>>> set('1234', 'item_use', url_name='item_use_execute', url_args=[10], message='spam')
True
>>> get('1234', 'item_use').path
'/m/item/use/execute/10'
>>> get('1234', 'item_use').message
'spam'
>>> delete('1234', 'home')
>>> get('1234', 'item_use')
None

"""
from gtoolkit.path_container.container import PathContainer

__all__ = ['set', 'get', 'delete']


def set(player_id, container_key, url_name, url_args=None, message=''):
    """
    Pathを保存

    :param player_id: プレイヤーID
    :type player_id: string

    :param container_key: パスの格納キー
    :type container_key: string or list

    :param url_name: reverse()の第一引数
    :type url_name: string

    :param url_args: reverse()のargs
    :type url_args: list

    :param message: リンク文字列などを渡したい場合に
    :type message: string
    """
    return PathContainer(player_id, container_key).set(url_name, url_args,
                                                       message=message)


def get(player_id, container_key, delete=True):
    """
    保存したPathを取得

    :param player_id: プレイヤーID
    :type player_id: string

    :param container_key: パスの格納キー
    :type container_key: string or list

    :param delete: 取得後にデータを削除するか
    :type delete: bool

    :return: Path
    :rtype: PathContainer
    """
    return PathContainer.get(player_id, container_key, delete=delete)


def delete(player_id, container_key):
    """
    保存したPathを削除

    :param player_id: プレイヤーID
    :type player_id: string

    :param container_key: パスの格納キー
    :type container_key: string or list
    """
    return PathContainer(player_id, container_key).delete()
