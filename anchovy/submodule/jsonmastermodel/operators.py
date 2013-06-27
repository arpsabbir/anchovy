# -*- coding: utf-8 -*-
"""
JsonMasterModelで使用する比較条件

.objects.get(value__lte) objects.filter(value__gte)などのdjangoの
query比較演算を使用出来るようにする

"""


def _lte(v_1, v_2):
    return v_1 <= v_2

def _lt(v_1, v_2):
    return v_1 < v_2

def _gte(v_1, v_2):
    return v_1 >= v_2

def _gt(v_1, v_2):
    return v_1 > v_2

operators = {"__lte": _lte,
             "__lt": _lt,
             "__gte": _gte,
             "__gt": _gt,
             }

