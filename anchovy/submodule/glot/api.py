# -*- coding: utf-8 -*-
"""
API 関数は, api.py から __init__.py へ移動.
旧版との互換性の都合上, 残しておく.
"""

from . import init as new_init, get as new_get

def init(*args, **kwargs):
    return new_init(*args, **kwargs)

def get(*args, **kwargs):
    return int(new_get(*args, **kwargs))
