# coding: utf-8
from nose.tools import eq_
from mock import Mock
from datetime import datetime
from kome.core.actionlog import *
from kome.core.derivedlog import *

class TestDerivedLog:
    def _make_actlog(self):
        sender = Mock()
        uid = '012345678'
        device = 'iPhone'
        return ActionLog(sender, uid, device)

    def test___init__(self):
        actlog = self._make_actlog()
        record = actlog.log('test', arg1='hoge', arg2=100)
        actd = record.get_derivedlog()
        eq_('test', actd.parent_record.actname)
        eq_(actlog, actd.parent)

    def test_inc_money(self):
        now = datetime.now()
        actlog = self._make_actlog()
        record = actlog.log('test')
        actd = record.get_derivedlog()

        actd.inc_money(20, 120, 100, time=now)
        actd.parent.sender.emit.assert_called_with({
            'uid': actd.parent.uid,
            'ver': 2,
            'time': now,
            'device': 'iPhone',
            'parent': 'test',
            'parentid': actd.parent_record.id,
            'action': 'inc_money',
            'before_value': 20,
            'after_value': 120,
            'value': 100 })

    def test_log(self):
        now = datetime.now()
        actlog = self._make_actlog()
        record = actlog.log('test')
        actd = record.get_derivedlog()

        actd.log('test2', arg1='fuga', arg2=200, time=now)
        actd.parent.sender.emit.assert_called_with({
            'uid': actd.parent.uid,
            'ver': 2,
            'time': now,
            'device': 'iPhone',
            'parent': 'test',
            'parentid': actd.parent_record.id,
            'action': 'test2',
            'arg1': 'fuga',
            'arg2': 200 })

    def test_noparent(self):
        now = datetime.now()
        actlog = self._make_actlog()
        actd = DerivedLog(actlog, None)

        actd.log('test2', arg1='fuga', arg2=200, time=now)
        actd.parent.sender.emit.assert_called_with({
            'uid': actd.parent.uid,
            'ver': 2,
            'time': now,
            'device': 'iPhone',
            'action': 'test2',
            'arg1': 'fuga',
            'arg2': 200 })
