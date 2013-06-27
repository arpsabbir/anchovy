# -*- coding: utf-8 -*-
"""

    choice_ratio
    ~~~~~~~~~~~~

    割合でリストの中から一つ選ぶライブラリ

"""

import random


def choice_index_ratio(ratio_sequence):
    """ratio_sequence の割合を考慮し、どれか一つを選ぶ。

    :return: ratio_sequence のインデックス番号
    :rtype: int

    :param ratio_sequence: 割合整数のリスト。
    :type ratio_sequence: list

    10,10,80 のリストの場合、80%の確率で 2 が返される。

    >>> index = choice_index_ratio([10,20,30])
    >>> assert 0 <= index <= 2
    >>> index = choice_index_ratio([0,0])
    >>> assert index is None
    >>> choice_index_ratio([0,0,1])
    2
    >>> choice_index_ratio([0,100,0])
    1
    """
    total = 0
    total_list = []
    for ratio in ratio_sequence:
        total += int(ratio)
        total_list.append(total)
    if not total:
        return None
    r = random.randint(1, total)
    for i, v in enumerate(total_list):
        if v >= r:
            return i
    raise Exception('choice_index_ratio: choice error. ratio_sequence:{}'
                    .format(ratio_sequence))


def choice_by_ratio(seq, ratio_key):
    """シーケンスの中から割合を考慮し1つ選択する

    :type seq: list or tuple
    :type ratio_key: basestring or callable
        文字列の場合は、getattr して割合を探す

    :return: seq の中の一つ

    >>> L = [('apple', 10), ('banana', 20), ('cherry', 30)]
    >>> chosen = choice_by_ratio(L, lambda x:x[1])
    >>> chosen[0] in ('apple', 'banana', 'cherry')
    True

    >>> class Mock(object):
    ...     def __init__(self, name, ratio):
    ...         self.name = name
    ...         self.ratio = ratio
    ...
    >>> L = [Mock('ham', 3), Mock('egg', 0), Mock('spam', 5)]
    >>> chosen = choice_by_ratio(L, 'ratio')
    >>> chosen.name in ('ham', 'spam')
    True
    """
    if hasattr(ratio_key, '__call__'):
        # ratio_key がコーラブル(例:lambda式)ならそれを呼んで割合リストを作る
        ratio_list = [ratio_key(r) for r in seq]
    else:
        # そうでないなら getattr
        ratio_list = [getattr(r, ratio_key) for r in seq]
    index = choice_index_ratio(ratio_list)
    return seq[index]


def choice_index_ratio_or_defeat(ratio_sequence, default=None):
    """ratio_listの割合を考慮し、どれか一つを選ぶ。ハズレあり。

    0.5, 0.2 の場合、50% の確率で 0 が返り、
    30% の確率で None が返る

    浮動小数点計算なので若干の誤差が入る。

    :param ratio_sequence: 1 以下の float (割合)のリスト。
    :type ratio_sequence: list or tuple
    :param default: 抽選ハズレの場合に返されるもの

    :return: ratio_sequence のインデックス番号
    :rtype: int or None

    int のシーケンスだと raise する
    >>> choice_index_ratio_or_defeat([1, 2, 3])
    Traceback (most recent call last):
    ...
    TypeError: ratio type is not float. (1, <type 'int'>)

    合計値が1以上だと raise する
    >>> choice_index_ratio_or_defeat((0.5, 0.6,))
    Traceback (most recent call last):
    ...
    RuntimeError: ratio total too large. total=1.1

    確実に2が返ってくる
    >>> choice_index_ratio_or_defeat([0.0, 0.0, 1.0,])
    2

    確実にNone
    >>> choice_index_ratio_or_defeat((0.0, 0.0,)) is None
    True

    確実に 'D'
    >>> choice_index_ratio_or_defeat([0.0, 0.0,], default='D')
    'D'

    確実に 0 〜 3 が帰ってくると思うが、浮動小数点誤差により None かもしれない。
    ハズレなし抽選がしたい場合は choice_index_ratio を使うこと
    >>> i = choice_index_ratio_or_defeat([0.25, 0.25, 0.4, 0.1])
    >>> i in [0, 1, 2, 3]
    True

    浮動小数点誤差っぽい割合ならRaiseする
    >>> i = choice_index_ratio_or_defeat([0.25, 0.25, 0.4, 0.09999999])
    Traceback (most recent call last):
    ...
    RuntimeError: ratio has fudge factor. total=0.99999999
    """
    total = 0.0
    total_list = []
    for ratio in ratio_sequence:
        if not isinstance(ratio, float):
            raise TypeError('ratio type is not float. ({}, {})'.format(
                ratio, type(ratio)))
        total += ratio
        total_list.append(total)

    if total > 1.01:
        # totalが大きすぎる場合は停止する (1.0はOK)
        # 浮動小数点誤差があると思うので > 1 とはしないでおく
        raise RuntimeError('ratio total too large. total={}'.format(total))

    if 0.99999 < total < 1.0:
        # 微妙に 1.0 に達してない場合は、浮動小数点誤差があると思われるので
        # raiseしておく。
        raise RuntimeError('ratio has fudge factor. total={}'.format(total))

    r = random.random()
    for i, v in enumerate(total_list):
        if v >= r:
            return i
    return default


def choice_by_ratio_or_defeat(seq, ratio_key, default=None):
    """シーケンスの中から割合を考慮し1つ選択する

    割合は浮動小数点数でなければならず、ハズレる可能性もある。
    ハズレた場合は default が返る

    :type seq: list or tuple
    :type ratio_key: basestring or callable
        文字列の場合は、getattr して割合を探す

    :return: seq の中の一つ

    >>> L = [('apple', 0.3), ('banana', 0.5), ('cherry', 0.2)]
    >>> chosen = choice_by_ratio_or_defeat(L, lambda x:x[1])
    >>> chosen[0] in ('apple', 'banana', 'cherry')
    True

    >>> class Mock(object):
    ...     def __init__(self, name, ratio):
    ...         self.name = name
    ...         self.ratio = ratio
    ...
    >>> L = [Mock('ham', 0.4), Mock('egg', 0.0), Mock('spam', 0.6)]
    >>> chosen = choice_by_ratio_or_defeat(L, 'ratio')
    >>> chosen.name in ('ham', 'spam')
    True

    >>> L = [('apple', 0.0), ('banana', 0.0)]
    >>> choice_by_ratio_or_defeat(L, lambda x:x[1], default='D')
    'D'

    """
    if hasattr(ratio_key, '__call__'):
        # ratio_key がコーラブル(例:lambda式)ならそれを呼んで割合リストを作る
        ratio_list = [ratio_key(r) for r in seq]
    else:
        # そうでないなら getattr
        ratio_list = [getattr(r, ratio_key) for r in seq]
    index = choice_index_ratio_or_defeat(ratio_list)
    if index is None:
        return default
    else:
        return seq[index]
