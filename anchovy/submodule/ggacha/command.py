# -*- coding: utf-8 -*-
"""
ガチャのバックグランドプロセスを簡単に作成するためのクラスを提供する.
"""

import sys
import os
from signal import signal, SIGINT, SIGTERM

from django.core.management.base import NoArgsCommand

from ggacha.logic import BackgroundLogicMixin, DeadLetterLogicMixin

class BackgroundCommand(BackgroundLogicMixin, NoArgsCommand):
    """
    Django の manage.py から起動できるバックグラウンドプロセスを作成する際,
    management.commands.[command_name].Command クラスに継承するクラス.

    Command クラスを作成する例は下記の通り.

    .. code-block:: python

        from ggacha.command import BackgroundCommand
        from path.to.logic import FooLogicMixin

        class Command(FooLogicMixin, BackgroundCommand):
            help = u'Fooガチャ用のバックグラウンドプロセスを起動します'


    例の FooLogicMixin は, 必ず ggacha.logic.BackgroundLogicMixin のサブクラスである事.

    これで, manage.py [command_name] と実行すると,
    FooLogicMixin.queue_name という名前でキューを作成＆監視し, 
    キューにメッセージが届くと FooLogicMixin.do_gacha を実行するコマンドができる.

    Supervisor と組み合わせる事を想定しているため, デーモン化は行わない.
    """
    def handle_noargs(self, **options):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
        for sig in [SIGINT, SIGTERM]:
            signal(sig, self._handle_signal)
        print 'Started the background process.'
        self.start_worker()
        print 'Stopped the background process.'

    def _handle_signal(self, num, frame):
        print 'Trap SIGNAL: {}'.format(num)
        self.stop_worker()


class DeadLetterCommand(BackgroundCommand, DeadLetterLogicMixin):
    """
    Dead Letter を掃除するコマンド.
    drain(self, body) を上書きして使用する事.

    .. code-block:: python
        class Command(DeadLetterCommand):
            def drain(self, body):
                # メール等で body を送る
                self.write_log_debug(u'body: %s', body)
    """
    pass
