# coding: utf-8

from kome.core.plugin import plugin_manager

class Copy:
    """
    複数の出力へ出力するプラグイン
    """
    def __init__(self, config):
        self._outputs = [plugin_manager.get(cfg['type'])(cfg) for cfg in config['outputs']]

    def emit(self, data):
        for out in self._outputs:
            out.emit(data)

plugin_manager.register('copy', Copy)
