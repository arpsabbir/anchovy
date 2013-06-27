# -*- coding: utf-8 -*-
"""
Django Settings
"""

from gconf.dict import DictSettings

class _Settings(DictSettings):
    settings_name = 'GGACHA_SETTINGS'
    default_settings = {
        'MESSAGE_BROKER': 'amqp://guest:guest@localhost:5672//',
        'REDIS_DB': 'default',
        'BACKGROUND_OFF': False,
        'QUEUE_NAME_PREFIX': None,
    }

settings = _Settings()
