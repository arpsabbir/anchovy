# coding: utf-8

from datetime import datetime
from kome.core.types import *
from kome.core.types import _isinstance

class DerivedLog(object):
    def __init__(self, parent, parent_record):
        self._parent = parent
        self._parent_record = parent_record

    @property
    def parent(self):
        return self._parent

    @property
    def parent_record(self):
        return self._parent_record

    def log(self, actname, **kwargs):
        u"""
        任意の派生ログを出力する
        """
        # time が指定されている場合はそっちを優先する
        time = kwargs.get('time', datetime.now())

        record = dict(kwargs)
        record.update({
            'uid': self.parent.uid,
            'ver': self.parent.version,
            'time': time,
            'device': self.parent.device,
            'action': actname })

        if self.parent_record is not None:
            record.update({
                'parent': self.parent_record.actname,
                'parentid': self.parent_record.id })

        self.parent.sender.emit(record)

        return self

    #############################
    # 以下自動生成で出力した実装
    #############################
