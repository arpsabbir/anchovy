# coding: utf-8
from nose.tools import ok_, eq_
from mock import Mock
from kome.core.sender import Sender
from kome.core.actionlog import *
import syslog
import sys

class TestSender:
    def _make_actlog(self, config):
        sender = Sender(config)
        uid = '012345678'
        device = 'iPhone'
        return ActionLog(sender, uid, device)

    def test_emit(self):
        actlog = self._make_actlog({ 'type': 'stdout' })
        sys.stdout = Mock()
        actd = actlog.register(RegisterType.NORMAL, str='ほげ', uni=u'ふが')
        ok_(sys.stdout.write.called)

        actlog = self._make_actlog({ 'type': 'null' })
        actlog.sender._output.emit = Mock()
        actd = actlog.register(RegisterType.NORMAL, str='ほげ', uni=u'ふが')
        ok_(actlog.sender._output.emit.called)

        actlog = self._make_actlog({ 'type': 'copy',
                                     'outputs': [{ 'type': 'stdout' },
                                                 { 'type': 'syslogp' }] })
        actlog.sender._output._outputs[1].emit = Mock()
        sys.stdout = Mock()
        actd = actlog.register(RegisterType.NORMAL, str='ほげ', uni=u'ふが')
        ok_(sys.stdout.write.called)
        ok_(actlog.sender._output._outputs[1].emit.called)

    def test_fluent(self):
        actlog = self._make_actlog({ 'type': 'fluentp',
                                     'app': 'hoge' })
        actd = actlog.register(RegisterType.NORMAL, int=100, str='ほげ', uni=u'ふが')
