# -*- coding: utf-8 -*-
"""
submodules innodb_monitor への依存を, この module に集約する.
import できない場合, ダミーを定義する.
"""
from contextlib import contextmanager
from django.conf import settings

try:
    from innodb_monitor.django.exception import handle_dblock_exception
    from innodb_monitor.django.notifier.logger import notify as logger_notify
    from innodb_monitor.django.notifier.mail import notify as mail_notify
except ImportError:
    class handle_dblock_exception(object):
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self, *args, **kwargs):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            return True if exc_type is None else False

    def logger_notify(message):
        pass

    def mail_notify(message):
        pass


NOTIFIER = {
    'logger': logger_notify,
    'mail': mail_notify,
}


@contextmanager
def handle_dblock(db_names, commit_context):
    notify_method = getattr(settings, 'INNODB_MONITOR_NOTIFY_METHOD', 'logger')
    with handle_dblock_exception(db_names, NOTIFIER[notify_method]):
        with commit_context:
            yield
