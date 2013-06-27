# -*- coding: utf-8 -*-
"""
設定を取得するクラス.
"""

from gconf.dict import DictSettings

class Settings(DictSettings):
    settings_name = 'GTIMER_SETTINGS'
    default_settings = {
        'KEY_PREFIX': '',
        'DB': 'default',
    }
