# -*- coding: utf-8 -*-
u"""
    ハッシュ関数を元に、乱数っぽいものを作るライブラリ
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    正しくは乱数ではない。ハッシュのソースを元に、結果は一意に確定される。

    精度は多分低い

    >>> hashrandom('source-string').randint(0, 99999)
    86553

    この結果はソース文字列が変わらない限り何度やっても変わらない。

    すまぬ: このテストは64bitでないと成功しない
"""

import hashlib
import struct
import sys

is_python_64bit = sys.maxsize > 2 ** 32
binary_slice_size = 8 if is_python_64bit else 4


class HashRandom(object):
    """
    ハッシュ関数を元に、乱数っぽいものを作る

    :param source: ハッシュ元文字列
    """

    @property
    def _hash_engine(self):
        return hashlib.sha256

    def __init__(self, source):
        if not isinstance(source, basestring):
            source = str(source)
        self._hash_instance = self._hash_engine(source)
        self._randomized_long = struct.unpack(
            'L', self._hash_instance.digest()[:binary_slice_size])[0]

    def randint(self, a, b):
        u"""a <= 値 <= b になるような整数値を出力

        >>> hashrandom('a').randint(1, 1)
        1
        >>> hashrandom('b').randint(-100, 1)
        -90

        結果は long になることもある
        >>> hashrandom('a').randint(0, 99999999999999999999)
        14608863320967583690L

        >>> result_list = list()
        >>> for i in xrange(300):
        ...    result_list.append(hashrandom('xx{}'.format(i)).randint(0, 100))
        >>> all([0 <= x <= 100 for x in result_list])
        True

        >>> from collections import Counter
        >>> counter = Counter([hashrandom(str(i)).randint(0, 9)
        ...    for i in xrange(100000)])
        >>> sorted(counter.iteritems())
        [(0, 10041), (1, 10114), (2, 10032), (3, 10006), (4, 9863), (5, 9995), (6, 10062), (7, 9768), (8, 10151), (9, 9968)]
        """
        if a > b:
            raise ValueError('No {} <= {}.'.format(a, b))
        rng = b + 1 - a
        return int(a + (self._randomized_long % rng))

    def choice(self, sequence):
        u"""
        sequence から 1つを選択

        >>> hashrandom('x').choice(['a','b','c','d','e'])
        'b'
        >>> hashrandom('a').choice(['a'])
        'a'
        >>> hashrandom('b').choice(['a'])
        'a'

        >>> from collections import Counter
        >>> source = ['a', 'b', 'c', 'd', 'e']
        >>> counter = Counter([hashrandom(str(i)).choice(source)
        ...    for i in xrange(100000)])
        >>> sorted(counter.iteritems())
        [('a', 20036), ('b', 20176), ('c', 19800), ('d', 20157), ('e', 19831)]
        """
        index = self.randint(0, len(sequence) - 1)
        return sequence[index]

    def choice_index_ratio(self, ratio_sequence):
        u"""
        gtoolkit.math.choice_ratio.choice_index_ratio と同等機能を提供

        >>> hashrandom('a').choice_index_ratio([10,20,30])
        1
        >>> hashrandom('a').choice_index_ratio([0,0])

        >>> from collections import Counter
        >>> source = [50, 30, 15, 4, 1]
        >>> counter = Counter([hashrandom(str(i)).choice_index_ratio(source)
        ...    for i in xrange(100000)])
        >>> sorted(counter.iteritems())
        [(0, 50441), (1, 29646), (2, 14880), (3, 4062), (4, 971)]

        :param ratio_sequence: 割合のシーケンス
        :return: シーケンス中のインデックス
        :rtype: int
        """

        total = 0
        total_list = []
        for ratio in ratio_sequence:
            total += int(ratio)
            total_list.append(total)
        if not total:
            return None
        r = self.randint(1, total)
        for i, v in enumerate(total_list):
            if v >= r:
                return i
        raise Exception('choice_index_ratio: choice error. ratio_sequence:{}'
                        .format(ratio_sequence))

    def choice_by_ratio(self, seq, ratio_key):
        u"""
        シーケンスの中から割合を考慮し1つ選択する

        gtoolkit.math.choice_ratio.choice_index_ratio と同等機能を提供

        seq は、リストとかタプルとか
        ratio_key は、文字列かコーラブルオブジェクト(例:lambda)
        文字列の場合は、getattr して割合を探す

        :return: seq の中の一つ

        >>> L = [('apple', 10), ('banana', 20), ('cherry', 30)]
        >>> hashrandom('z').choice_by_ratio(L, lambda x:x[1])
        ('apple', 10)

        >>> class Mock(object):
        ...     def __init__(self, name, ratio):
        ...         self.name = name
        ...         self.ratio = ratio
        ...
        >>> L = [Mock('ham', 3), Mock('egg', 0), Mock('spam', 5)]
        >>> chosen = hashrandom('y').choice_by_ratio(L, 'ratio')
        >>> chosen.name
        'ham'

        >>> from collections import Counter
        >>> source = [('A', 1), ('B', 199), ('C', 800)]
        >>> counter = Counter([hashrandom(str(i)).choice_by_ratio(
        ...    source, lambda x: x[1]) for i in xrange(100000)])
        >>> sorted(counter.iteritems())
        [(('A', 1), 81), (('B', 199), 19801), (('C', 800), 80118)]
        """
        if hasattr(ratio_key, '__call__'):
            # ratio_key がコーラブル(例:lambda式)なら
            # それを呼んで割合リストを作る
            ratio_list = [ratio_key(r) for r in seq]
        else:
            # そうでないなら getattr
            ratio_list = [getattr(r, ratio_key) for r in seq]
        index = self.choice_index_ratio(ratio_list)
        return seq[index]


hashrandom = HashRandom