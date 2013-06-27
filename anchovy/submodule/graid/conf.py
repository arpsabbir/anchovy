# -*- coding: utf-8 -*-
"""
設定を取得するクラス.
"""

from gconf.dict import DictSettings

class GraidSettings(DictSettings):
    settings_name = 'GRAID_SETTINGS'
    default_settings = {
        'KEY_PREFIX': '',
        'DB': 'default',
    }
