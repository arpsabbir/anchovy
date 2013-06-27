# -*- coding: utf-8 -*-
"""
ガチャ用の Supervisord 設定ファイルを生成する
"""
import copy

from django.core.management.base import BaseCommand
from django.template import loader, Context


class GenerateSupervisordConfigCommand(BaseCommand):
    """
    settings.TEMPLATE_DIRS に 'ggacha/supervisord/template' を追加する事.
    """
    help = u'ガチャ用の Supervisord 設定ファイルを生成する'

    _unix_http_server = {'file': '/tmp/supervisor.sock',}
    _inet_http_server = {'port': '0.0.0.0:9001',}
    _supervisorctl = {'serverurl': 'unix:///tmp/supervisor.sock',}

    _supervisord = {'logfile_maxbytes': '5MB',
                    'logfile_backups': 200,
                    'loglevel': 'info',
                    'pidfile': '/var/run/supervisord.pid',
                    'nodaemon': 'false',}

    _environment = {'logpath': '/var/log/supervisor',
                    'user': 'webapp',
                    'stdout_logfile_maxbytes': '5MB',
                    'stdout_logfile_backups': 200,}

    _process = {'priority': 500,
                'numprocs': 2,}

    def handle(self, *args, **options):
        """
        条件により動作を変更する場合, このメソッドを上書きする事.
        """
        print self.generate_config()

    def generate_config(self):
        self._validate()
        t = loader.get_template('root.conf')
        return t.render(Context(self._get_config()))

    def _validate(self):
        for key in ['home', 'path', 'virtual_env', 'settings']:
            assert self.environment[key]

        assert len(self.processes)
        for process in self.processes:
            for key in ['name', 'command']:
                assert process[key]

    def _get_config(self):
        config = {name: self._get_attr(name)
                  for name in ['unix_http_server',
                               'inet_http_server',
                               'supervisorctl',
                               'supervisord',
                               'environment',]}

        config['processes'] = []
        for process in self.processes:
            use_process = copy.copy(self._process)
            use_process.update(process)
            config['processes'].append(use_process)

        return config

    def _get_attr(self, name):
        default_name = '_' + name
        value = getattr(self, default_name)
        value.update(getattr(self, name, {}))
        return value
