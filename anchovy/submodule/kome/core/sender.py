# coding: utf-8

from kome.core.plugin import plugin_manager

class Sender:
    def __init__(self, config):
        """
        { 'type': 'syslog',
          'logname': 'logname',
          ... }
        """
        self._output = plugin_manager.get(config['type'])(config)

    def emit(self, data):
        self._output.emit(data)

