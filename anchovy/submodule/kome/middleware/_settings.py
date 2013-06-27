#coding: utf-8

_KOME_INFO = None
try:
    from django.conf import settings
    _KOME_INFO = settings.KOME_INFO
except:
    pass

def is_debug():
    try:
        return _KOME_INFO['debug']
    except:
        return False

def get_config():
    try:
        return _KOME_INFO['config']
    except:
        return None

def get_osuserid():
    try:
        return _KOME_INFO['osuserid']
    except:
        return None
