# -*- coding: utf-8 -*-

"""
ムービーごとの変数:実際に置き換える時のID(変数名)の対応表
{
    ムービー名: {
        ムービー種類(ex. html,swf): {
            変数名(ex. card_image1): 変換先変数名(24),
            ...
        },
        ...
    },
}
"""
import os
from django.utils import simplejson

DEFAULT_ANIMATION_TYPES = ['swf', 'html']
MAP_FILE_SUFFIX = '.idmap'

MOVIE_PARAM_MAP = {
}

try:
    from extension.animation_params import EXTERNAL_MOVIE_PARAM_MAP
except ImportError:
    EXTERNAL_MOVIE_PARAM_MAP = None


def get_param(movie_name, movie_type, param):
    # Extensionがあればそちらで上書きする
    if EXTERNAL_MOVIE_PARAM_MAP and movie_name in EXTERNAL_MOVIE_PARAM_MAP:
        ex_param = EXTERNAL_MOVIE_PARAM_MAP[movie_name]

        if ex_param and isinstance(ex_param, dict) and param and isinstance(param, dict):
            param.update(ex_param[movie_type])
        elif ex_param:
            param = ex_param[movie_type]

    return param


class AnimationParamDuplicateDefinitionError(Exception):
    pass


def register_animation_param_map(movie_name, swf=None, html=None, reel=None):
    """
    ムービーの変数マップを登録
    """
    if movie_name in MOVIE_PARAM_MAP:
        # 二重定義
        raise AnimationParamDuplicateDefinitionError(movie_name)

    MOVIE_PARAM_MAP[movie_name] = {
        'swf': get_param(movie_name, 'swf', swf),
        'html': get_param(movie_name, 'html', html),
        'reel': get_param(movie_name, 'reel', reel),
    }


def get_animation_param_name(movie_name, type, name):
    """
    ムービーの変数マップを返す
    """
    try:
        return MOVIE_PARAM_MAP[movie_name][type][name]
    except KeyError:
        return None


class IdMapDoesNotExist(Exception):
    pass


def load_animation_id_map(movie_name, animation_types=None):
    u"""
    各ムービー(swfなど)の隣にある、.idmap.json をロードする

    例::

        load_animation_id_map('quest/quest', animation_types=['swf', 'html'])

    :param movie_name: 'quest/quest' とか
    :param animation_types: ['swf', 'html', 'reel'] のようなシーケンス
        無ければ swf と html の2種
    :return: None
    """
    if movie_name in MOVIE_PARAM_MAP:
        #  既にロード済み
        return

    from gtoolkit.animation.render import ANIMATION_BASE_PATH

    animation_types = animation_types or DEFAULT_ANIMATION_TYPES

    register = dict()
    # ↑最終的にこんなdictになる:
    # {
    #   'swf': {'bg': 1, ...},
    #   'html': {'bg': 4, ...},
    #   'reel': {'bg': 18, ...},
    # }

    for animation_type in animation_types:
        # idmap.json の場所をループして探す。無ければ何もしない
        idmap_path = os.path.join(
            ANIMATION_BASE_PATH,
            animation_type,
            movie_name + MAP_FILE_SUFFIX)
        try:
            fp = open(idmap_path)
        except IOError:
            raise IdMapDoesNotExist(idmap_path)
        else:
            id_map = simplejson.load(fp)
            register[animation_type] = id_map
            fp.close()

    # 登録
    register_animation_param_map(movie_name, **register)