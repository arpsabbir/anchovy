# -*- coding: utf-8 -*-
"""
設定を取得するクラス.
"""

from gconf.dict import DictSettings

class Settings(DictSettings):
    settings_name = 'GRANKING'
    default_settings = {
        'KEY_PREFIX': '',
        'DB': 'default',
        'EXPIRE': 60 * 60 * 24 * 14, # 2 weeks
    }
