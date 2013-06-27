# coding: utf-8

from nose.tools import ok_, eq_, raises
from mock import Mock, call
from kome.middleware import actionlog as mw
from kome.middleware import _settings
from kome.core.actionlog import *

class TestMiddlewareActionLog:
    def teardown(self):
        mw.sender = mw._null_sender

    def test_globals(self):
        eq_(mw.sender, mw._null_sender)

    def _to_debug_mode(self):
        _settings.is_debug = lambda: True

    def _to_no_debug_mode(self):
        _settings.is_debug = lambda: False

    @raises(AttributeError)
    def test_raise_noexists_method(self):
        mw.log().notexists_method()

    @raises(TypeError)
    def test_raise_arg_not_enough(self):
        self._to_debug_mode()

        #raise TypeError('%s() takes %s %d %s (%d given)' % (
        #    f_name, 'at least' if defaults else 'exactly', num_required,
        #    'arguments' if num_required > 1 else 'argument', num_total))
        with mw.log().register():
            pass

    def _init_request(self):
        request = Mock()
        request.META = {
            'HTTP_USER_AGENT': 'KDDI-SA31 UP.Browser/6.2.0.6.3.129 (GUI) MMP/2.0'
        }
        request.opensocial_viewer_id = '12345678'
        actlogmw = mw.ActionLogMiddleware()
        mw.sender = Mock()
        actlogmw.process_request(request)
        return (actlogmw, request)

    def test_process_response(self):
        (actlogmw, request) = self._init_request()
        actlogmw.process_response(request, None)

    def test_log(self):
        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id = 'id'
        id2 = 'id2'

        with mw.log().log('log1', x=10, y='str', id=id, time=now):
            mw.log().derivedlog.log('dlog1', z=10, time=now)
            with mw.log().log('log2', id=id2, time=now):
                mw.log().set(z=100)
                mw.log().derivedlog.log('dlog2', time=now)
            mw.log().derivedlog.log('dlog3', time=now)


        actlogmw.process_response(request, None)

        log1 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'id': id,
                 'action': 'log1',
                 'x': 10,
                 'y': 'str' }
        dlog1 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id,
                  'parent': 'log1',
                  'action': 'dlog1',
                  'z': 10 }
        dlog3 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id,
                  'parent': 'log1',
                  'action': 'dlog3' }
        log2 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'parentid': id,
                 'parent': 'log1',
                 'id': id2,
                 'action': 'log2',
                 'z': 100 }
        dlog2 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id2,
                  'parent': 'log2',
                  'action': 'dlog2' }
        expected = [call.emit(log1),
                    call.emit(dlog1),
                    call.emit(dlog3),
                    call.emit(log2),
                    call.emit(dlog2)]
        eq_(expected, mw.sender.mock_calls)

    def test_log_except_partial(self):
        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id = 'id'
        id2 = 'id2'

        with mw.log().log('log1', x=10, y='str', id=id, time=now):
            mw.log().derivedlog.log('dlog1', z=10, time=now)
            try:
                with mw.log().log('log2', id=id2, time=now):
                    mw.log().derivedlog.log('dlog2', time=now)
                    raise Exception
            except:
                pass
            mw.log().derivedlog.log('dlog3', time=now)

        actlogmw.process_response(request, None)

        log1 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'id': id,
                 'action': 'log1',
                 'x': 10,
                 'y': 'str' }
        dlog1 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id,
                  'parent': 'log1',
                  'action': 'dlog1',
                  'z': 10 }
        dlog3 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id,
                  'parent': 'log1',
                  'action': 'dlog3' }
        expected = [call.emit(log1),
                    call.emit(dlog1),
                    call.emit(dlog3)]
        eq_(expected, mw.sender.mock_calls)

    def test_log_except_all(self):
        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id = 'id'
        id2 = 'id2'

        try:
            with mw.log().log('log1', x=10, y='str', id=id, time=now):
                mw.log().derivedlog.log('dlog1', z=10, time=now)
                with mw.log().log('log2', id=id2, time=now):
                    mw.log().derivedlog.log('dlog2', time=now)
                    raise Exception
                mw.log().derivedlog.log('dlog3', time=now)
        except:
            pass

        actlogmw.process_response(request, None)

        eq_([], mw.sender.mock_calls)

    @mw.deco.log('log1')
    def _log1func(self, now, id, id2):
        mw.log().set(x=10, y='str', id=id, time=now)
        mw.log().derivedlog.log('dlog1', z=10, time=now)
        self._log2func(now, id, id2)
        mw.log().derivedlog.log('dlog3', time=now)

    @mw.deco.log('log2')
    def _log2func(self, now, id, id2):
        mw.log().set(id=id2, time=now)
        mw.log().set(z=100)
        mw.log().derivedlog.log('dlog2', time=now)

    def test_log_decorator(self):
        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id = 'id'
        id2 = 'id2'

        mw.log().set(a=1, x=20, y=100, z=3000)
        #mw.log().log('log1')(self._log1func)(now, id, id2)
        #mw.deco.log('log1')(_log1func)(now, id, id2)
        self._log1func(now, id, id2)

        actlogmw.process_response(request, None)

        log1 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'id': id,
                 'action': 'log1',
                 'x': 10,
                 'y': 'str' }
        dlog1 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id,
                  'parent': 'log1',
                  'action': 'dlog1',
                  'z': 10 }
        dlog3 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id,
                  'parent': 'log1',
                  'action': 'dlog3' }
        log2 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'parentid': id,
                 'parent': 'log1',
                 'id': id2,
                 'action': 'log2',
                 'z': 100 }
        dlog2 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id2,
                  'parent': 'log2',
                  'action': 'dlog2' }
        expected = [call.emit(log1),
                    call.emit(dlog1),
                    call.emit(dlog3),
                    call.emit(log2),
                    call.emit(dlog2)]
        eq_(expected, mw.sender.mock_calls)

    def test_named_log_decorator(self):
        @mw.deco.do_gacha()
        def testfunc():
            return 42
        value = testfunc()
        eq_(42, value)

    def test_call_process_response_when_do_not_call_process_request(self):
        request = Mock()
        request.META = {
            'HTTP_USER_AGENT': 'KDDI-SA31 UP.Browser/6.2.0.6.3.129 (GUI) MMP/2.0'
        }
        request.opensocial_viewer_id = '12345678'
        actlogmw = mw.ActionLogMiddleware()

        # Test nothing to raise.
        actlogmw.process_response(request, None)

    def test_call_process_response_without_opensocial_viewer_id(self):
        request = Mock()
        request.META = {
            'HTTP_USER_AGENT': 'KDDI-SA31 UP.Browser/6.2.0.6.3.129 (GUI) MMP/2.0'
        }
        actlogmw = mw.ActionLogMiddleware()
        actlogmw.process_request(request)

        # Test nothing to raise.
        actlogmw.process_response(request, None)

    def test_null_log(self):
        # Test nothing to raise
        logf = mw.log

        from kome.middleware.null_log_context import NullLogContext
        null_log_context = NullLogContext()
        mw.log = lambda: null_log_context

        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id = 'id'
        id2 = 'id2'

        self._log1func(now, id, id2)

        mw.log = logf

    def test_traceback(self):
        self._to_no_debug_mode()

        (actlogmw, request) = self._init_request()
        with mw.log().register():
            pass
        actlogmw.process_response(request, None)

    def test_noparent_derivedlog(self):
        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id = 'id'

        mw.log().derivedlog.log('dlog1', z=10, time=now)

        actlogmw.process_response(request, None)

        mw.sender.emit.assert_called_with({
            'uid': '12345678',
            'ver': 2,
            'time': now,
            'device': DeviceType.FP,
            'action': 'dlog1',
            'z': 10 })

    def test_continuous_log(self):
        (actlogmw, request) = self._init_request()

        now = datetime.now()
        id2 = 'id2'

        with mw.log().log('log1', x=10, y='str', time=now):
            uid = request.action_logger.uid
            device = request.action_logger.device
            actname = mw.log().actname
            actid = mw.log().id

        actlogmw.process_response(request, None)

        with mw.ActionLogger(mw.sender, uid, device, actname, actid):
            mw.log().derivedlog.log('dlog1', z=10, time=now)
            with mw.log().log('log2', id=id2, time=now):
                mw.log().set(z=100)
                mw.log().derivedlog.log('dlog2', time=now)

        log1 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'id': actid,
                 'action': 'log1',
                 'x': 10,
                 'y': 'str' }
        dlog1 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': actid,
                  'parent': 'log1',
                  'action': 'dlog1',
                  'z': 10 }
        log2 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'parentid': actid,
                 'parent': 'log1',
                 'id': id2,
                 'action': 'log2',
                 'z': 100 }
        dlog2 = { 'uid': '12345678',
                  'ver': 2,
                  'time': now,
                  'device': DeviceType.FP,
                  'parentid': id2,
                  'parent': 'log2',
                  'action': 'dlog2' }
        expected = [call.emit(log1),
                    call.emit(dlog1),
                    call.emit(log2),
                    call.emit(dlog2)]
        eq_(expected, mw.sender.mock_calls)

    def test_decorator(self):
        request = Mock()
        request.META = {
            'HTTP_USER_AGENT': 'KDDI-SA31 UP.Browser/6.2.0.6.3.129 (GUI) MMP/2.0'
        }
        request.opensocial_viewer_id = '12345678'

        mw.action_log_decorator_initialized = False

        now = datetime.now()
        id = 'id'

        @mw.action_log_decorator
        def logging(request):
            with mw.log().log('log1', x=10, y='str', id=id, time=now):
                pass

        mw.sender = Mock()

        logging(request)

        log1 = { 'uid': '12345678',
                 'ver': 2,
                 'time': now,
                 'device': DeviceType.FP,
                 'id': id,
                 'action': 'log1',
                 'x': 10,
                 'y': 'str' }
        expected = [call.emit(log1)]
        eq_(expected, mw.sender.mock_calls)
