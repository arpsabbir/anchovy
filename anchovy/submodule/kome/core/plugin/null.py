# coding: utf-8

from kome.core.plugin import plugin_manager

class Nullout:
    """
    何もしないプラグイン
    """
    def __init__(self, config):
        pass

    def emit(self, data):
        pass

plugin_manager.register('null', Nullout)
