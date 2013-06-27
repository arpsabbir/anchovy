# coding: utf-8

import time
from kome.core.plugin import plugin_manager
import fluent.sender

class Fluent:
    """
    fluentへ出力するプラグイン
    """
    def __init__(self, config):
        """
        { 'app': 'app',                  # require
          'host': 'localhost',           # optional
          'port': 24224 }                # optional

        receiver's fluentd.conf example:
            # fluent.py プラグインのデータを受け取るには forward を指定する必要がある
            <source>
                type forward
            </source>

            # payアクションだけ別の場所に流したい場合はこうする
            # app という文字列は config で指定したアプリケーション名
            <match kome.app.pay>
                host payonly
                port 24224
            </match>

            # 通常のアクションはこちらに流す
            <match kome.app.**>
                host 127.0.0.1
                port 24224
            </match>
        """
        # default
        host = config.get('host', 'localhost')
        port = config.get('port', 24224)
        self._sender = fluent.sender.FluentSender('kome', host=host, port=port)
        self._app = config['app'].replace('.', '_') # '.' must not be included.

    def emit(self, data):
        (action, timestamp, message) = self._make_message(data)
        self._sender.emit_with_time('.'.join((self._app, action)), timestamp, message)

    def _make_message(self, data):
        """
        出力用のメッセージを生成
        """
        action = data['action']
        timestamp = int(time.mktime(data['time'].timetuple()))
        message = dict([(k,repr(v)) for (k,v) in data.items()
                        if k != 'uid' and k != 'time' and k != 'action'])
        message['uid'] = str(data['uid'])

        return (action, timestamp, message)

plugin_manager.register('fluentp', Fluent)
