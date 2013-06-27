# coding: utf-8

import syslog
from kome.core.plugin import plugin_manager

class Syslog:
    """
    syslogへ出力するプラグイン
    """
    def __init__(self, config):
        """
        { 'app': 'app',                  # require
          'option': syslog.LOG_NOWAIT,   # optional
          'facility': syslog.LOG_LOCAL5, # optional
          'priority': syslog.LOG_INFO,   # optional
          'separator': '\t' }            # optional
        """
        # default
        self.config = { 
          'option': syslog.LOG_NOWAIT,
          'facility': syslog.LOG_LOCAL5,
          'priority': syslog.LOG_INFO,
          'separator': '\t' }
        self.config.update(config)

    def emit(self, data):
        message = self._make_message(data)
        cfg = self.config
        syslog.openlog(cfg['app'], cfg['option'], cfg['facility'])
        syslog.syslog(cfg['priority'], message)
        syslog.closelog()

    def _make_message(self, data):
        """
        出力用のメッセージを生成
        """
        sep = self.config['separator']

        xs = []
        for (k,v) in data.items():
            if k == 'time' or k == 'uid' or k == 'action':
                continue
            xs.append('[%s]%s%s' % (k, sep, repr(v)))
        message = '%s%s%s%s%s' % (data['action'], sep, data['uid'], sep, sep.join(xs))

        return message

plugin_manager.register('syslogp', Syslog)
