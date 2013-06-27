# coding: utf-8

import uuid
from datetime import datetime
import kome.core.sender
from kome.core.derivedlog import DerivedLog
from kome.core.types import *
from kome.core.types import _isinstance

class ActionRecord(object):
    def __init__(self, id, actname, time, action):
        self._actname = actname
        self._id = id
        self._time = time
        self._action = action

    @property
    def action(self):
        return self._action

    @property
    def id(self):
        return self._id

    @property
    def time(self):
        return self._time

    @property
    def actname(self):
        return self._actname

    def get_actlog(self):
        return ActionLog(
            self._action.sender,
            self._action.uid,
            self._action.device,
            self)

    def get_derivedlog(self):
        return DerivedLog(self._action, self)

class ActionLog(object):
    def __init__(self, sender, uid, device, parent_record = None):
        u"""
        アクションログの初期化

        sender -- ログの送信先
        uid    -- ユーザID
        device -- デバイス名
        parent_record -- 親アクション
        """
        self._sender = sender
        self._uid = uid
        self._device = device
        self._parent_record = parent_record

    @property
    def sender(self):
        return self._sender

    @property
    def uid(self):
        return self._uid

    @property
    def device(self):
        return self._device

    @property
    def version(self):
        return 2

    @property
    def parent_record(self):
        return self._parent_record

    def log(self, actname, **kwargs):
        u"""
        任意のログを出力する
        """
        # id が指定されている場合はそっちを優先する
        id = kwargs.get('id', str(uuid.uuid4()))
        # time が指定されている場合はそっちを優先する
        time = kwargs.get('time', datetime.now())

        record = dict(kwargs)
        record.update({
            'uid': self.uid,
            'ver': self.version,
            'time': time,
            'device': self.device,
            'action': actname,
            'id': id })
        if self.parent_record != None:
            record.update({
                'parent': self.parent_record.actname,
                'parentid': self.parent_record.id })

        self._sender.emit(record)

        return ActionRecord(id, actname, time, self)

    def _or_none(self, f):
        return lambda xs: xs is None or f(xs)

    def _string_list(self, xs):
        return _isinstance(xs, list) and \
               all([_isinstance(x, StringTypes) for x in xs])

    def _is_trade_items(self, xs):
        return self._string_list(xs)

    #############################
    # 以下自動生成で出力した実装
    #############################
