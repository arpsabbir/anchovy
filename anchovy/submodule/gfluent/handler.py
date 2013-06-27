# -*- coding: utf-8 -*-
import logging
import socket

from gfluent import sender

class FluentRecordFormatter(object):
    def __init__(self):
        self.hostname = socket.gethostname()

    def format(self, record):
        data = {
            'sys': {
                'level': record.levelname,
                'host': self.hostname,
                'name': record.name,
                'process': {
                    'no': record.process,
                    'name': record.processName,
                },
                'thread': {
                    'no': record.thread,
                    'name': record.threadName,
                },
                'caller': {
                    'path': record.pathname,
                    'lineno': record.lineno,
                    'module': record.module,
                    'function': record.funcName,
                },
            },
        }
        self._structuring(data, record)
        return data

    def _structuring(self, data, record):
        msg = record.msg
        if isinstance(msg, dict):
            self._add_dic(data, msg)
        elif isinstance(msg, (str, unicode)):
            self._add_dic(data, {'message': record.getMessage()})

    def _add_dic(self, data, dic):
        for k, v in dic.items():
            if isinstance(k, str) or isinstance(k, unicode):
                data[str(k)] = v


class FluentHandler(logging.Handler):
    '''
    Logging Handler for fluent.
    '''
    def __init__(self,
           tag,
           host='localhost',
           port=24224,
           timeout=3.0,
           verbose=False):

        self.tag = tag
        self.sender = sender.FluentSender(tag,
                                          host=host, port=port,
                                          timeout=timeout, verbose=verbose)
        self.fmt = FluentRecordFormatter()
        logging.Handler.__init__(self)

    def emit(self, record):
        if record.levelno < self.level: return
        data = self.fmt.format(record)
        self.sender.emit(record.name, data)

    def _close(self):
        self.sender._close()
