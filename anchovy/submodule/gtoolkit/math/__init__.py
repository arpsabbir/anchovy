# -*- coding: utf-8 -*-
"""
パラメータ計算用の曲線関数を生成してくれる
"""

from gtoolkit.math.graph_types import (GraphType1, GraphType2, 
                                       GraphType3, GraphType4,
                                       GraphType5)
from gtoolkit.math.bezier import Bezier

_graph_types = {
    1: GraphType1,
    2: GraphType2,
    3: GraphType3,
    4: GraphType4,
    5: GraphType5,
    }

def _dict_map(target_dict, f):
    result_dict = {}
    for k, v in target_dict.iteritems():
        result_dict[k] = f(v)
    return result_dict

def parameter_factory(graph_type=1,
                      k=1.0,
                      min_x=0.0, max_x=1.0,
                      min_y=0.0, max_y=1.0):
    """
    曲線の形を指定して関数を生成する

    :param int graph_type: グラフの形
    :param float k: 曲率
    :param float min_x: xの最小値
    :param float max_x: xの最大値
    :param float min_y: yの最小値
    :param float max_y: yの最大値
    :return: GraphTypeNのインスタンスを返す
    :raises: NameError(指定されたgraph_typeの関数が無い場合)

    >>> from gtoolkit.math import parameter_factory
    >>> 
    >>> param = parameter_factory(3)
    >>> param.get(1.0)
    
    get()の引数はxの値を渡す
    """
    return _parameter_factory(graph_type=graph_type,
                              k=k,
                              min_x=min_x, max_x=max_x,
                              min_y=min_y, max_y=max_y)

def _parameter_factory(graph_type=1, **kwargs):
    if graph_type not in _graph_types:
        raise NameError, 'GraphType%s not found.' % graph_type

    func = _graph_types[graph_type]
    kwargs = _dict_map(kwargs, lambda v: float(v))
    return func(**kwargs)

def bezier_factory(x1=0.5, y1=0.0,
                   x2=0.0, y2=0.5,
                   min_x=0.0, max_x=1.0,
                   min_y=0.0, max_y=1.0,
                   eps=0.001):
    """
    ベジエ曲線関数を生成する

    :param float x1: 第1制御点のx座標
    :param float y1: 第1制御点のy座標
    :param float x2: 第2制御点のx座標
    :param float y2: 第2制御点のy座標
    :param float min_x: xの最小値
    :param float max_x: xの最大値
    :param float min_y: yの最小値
    :param float max_y: yの最大値
    :param float eps: 曲線上の点を二分探索で求める際のしきい値
    :return: Bezierのインスタンスを返す

    >>> from gtoolkit.math import bezier_factory
    >>> 
    >>> param = bezier_factory()
    >>> param.get(1.0)

    get()の引数はxの値を渡す
    """
    return _bezier_factory(x1=x1, y1=y1,
                           x2=x2, y2=y2,
                           min_x=min_x, max_x=max_x,
                           min_y=min_y, max_y=max_y,
                           eps=eps)

def _bezier_factory(**kwargs):
    kwargs = _dict_map(kwargs, lambda v: float(v))
    return Bezier(**kwargs)
