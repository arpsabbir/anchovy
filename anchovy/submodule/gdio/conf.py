# -*- coding: utf-8 -*-
"""
設定を取得するクラス.
"""

from gconf.dict import DictSettings

class gDIOSettings(DictSettings):
    settings_name = 'GDIO_SETTINGS'
    default_settings = {
        'KEY_PREFIX': '',
        'DB': 'default',
    }
