# -*- coding:utf-8 -*-

import os


def abs_parent_path(path, up_level=1):
    u"""
    あるパスの上位パスを絶対パスで取得

    :param path: 元のパス文字列。大抵は __file__ を渡す
    :param up_level: どこまで上へいくか
    :return: パス文字列
    :rtype: str

    例::

        abs_parent_path(__file__, up_level=2)

    >>> abs_parent_path('/home/alice/data/document.txt', up_level=2)
    '/home'
    """
    # 上位ディレクトリを取得するには、os.path.pardir を加えて os.path.normpath
    # する方法もある。
    return os.path.sep.join(
        os.path.dirname(
            os.path.abspath(path)
        ).split(os.path.sep)[:-up_level]
    )
