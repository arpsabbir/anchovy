# coding: utf-8

from kome.core.plugin import plugin_manager

class Stdout:
    """
    標準出力へ出力するプラグイン
    """
    def __init__(self, config):
        pass

    def emit(self, data):
        print data

plugin_manager.register('stdout', Stdout)
