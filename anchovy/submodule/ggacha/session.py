# -*- coding: utf-8 -*-
"""
セッション関連の処理をまとめる.
"""
import msgpack

from ggacha.utils import RaiseExceptionMixin, HasKeyPrefix


class SessionMixin(RaiseExceptionMixin):
    """
    セッション操作用のトレイト.
    django の request に msgpack をかぶせてるだけ.
    キー名を View と GachaLogic で共用する目的で定義した.
    """
    class _Session(HasKeyPrefix):
        class _Result(object):
            def __init__(self, result):
                self._result = result

            def is_foreground(self):
                return self._is('foreground')

            def is_background(self):
                return self._is('background')

            def is_error(self):
                return self._is('error')

            def _is(self, on):
                if self._result['work_on'] == on:
                    return True
                else:
                    return False

            def result(self):
                return self._result['result']


        def __init__(self, session, gacha_id, player_id):
            self._session = session
            self.set_key_prefix(gacha_id, player_id)

        def get(self, key):
            value = self._session.get(self.build_key(key))
            if value is None:
                return None

            return msgpack.unpackb(value)

        def set(self, key, value):
            self._session[self.build_key(key)] = msgpack.packb(value)

        def delete(self, key):
            if self.get(key):
                del self._session[self.build_key(key)]

        def get_result(self):
            result = self.get('result')
            return self._Result(result) if result is not None else None

        def set_foreground_result(self, result):
            return self.set('result', {
                'work_on': 'foreground',
                'result': result,
            })

        def set_background_result(self, result):
            return self.set('result', {
                'work_on': 'background',
                'result': result,
            })

        def set_error_result(self, result):
            return self.set('result', {
                'work_on': 'error',
                'result': result,
            })

        def delete_result(self):
            self.delete('result')
 

    def init_session(self, request, gacha_id, player_id):
        self._session = self._Session(request.session, gacha_id, player_id)

    @property
    def session(self):
        self.raise_if_none('_session')
        return self._session
