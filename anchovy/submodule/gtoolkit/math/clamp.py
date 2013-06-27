# -*- coding: utf-8 -*-


def clamp(value, min_value, max_value):
    """
    min_value <= value <= max_value
    となるよう、値を丸めて返す。

    >>> clamp(12, 0, 100)
    12

    >>> clamp(-2, 10, 20)
    10

    >>> clamp(21, 10, 20)
    20

    """
    return min(max(min_value, value), max_value)