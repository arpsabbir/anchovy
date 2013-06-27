# -*- coding: utf-8 -*-
"""
cProfile でプロファイリングする.

アプリ側の準備
--------------

プロファイルを取得したい View の継承ツリーに混ぜる.

.. code-block:: python

    from gtoolkit.profile import ProfileView

    class SpamView(ProfileView):
        pass


Django Settings に設定を追加する.

.. code-block:: python

    GTOOLKIT_PROFILE_VIEWS = ['apps.website.v_root.views.RootHomeView']
    GTOOLKIT_PROFILE_HOSTS = ['neoyakuza-app1.gu3.jp']
    GTOOLKIT_PROFILE_PATH = '/tmp/profile'


GTOOLKIT_PROFILE_VIEWS
    本モジュールを使用する View 名の一覧.
    このリストに含まれる View のみプロファイルを取得する.
    プロファイルを取得すると負荷が掛かるので気をつける事.

GTOOLKIT_PROFILE_HOSTS
    本モジュールを使用するホスト名の一覧.
    このリストに含まれるホストでのみプロファイルを取得する.
    未指定であれば, 全ホストでプロファイルの取得を行う.

GTOOLKIT_PROFILE_PATH
    プロファイルファイルの保存先.
    省略すると, '/tmp/profile' となる.


ツールの準備
------------

KCacheGrind と pyprof2calltree をインストールする.
サーバにはインストールしない事!!

.. code-block:: shell

    $ port install kcachegrind
    $ pip install pyprof2calltree


確認
----

出力されたプロファイルデータを KCacheGrind で使用できる形式に変換する.

.. code-block:: shell

    $ pyprof2calltree -i /tmp/profile/view_name/epoch_time.profile -o ./callgrind.out


変換したファイルを KCacheGrind で表示する.

.. code-block:: shell

    $ kcachegrind ./callgrind.out


参考
----

http://99blues.dyndns.org/blog/2010/07/kcachegrind/
"""
from __future__ import absolute_import

import os
import sys
import socket
import cProfile
from functools import wraps
import time
import inspect

from django.conf import settings
from django.views.generic.base import View

from gtoolkit import datetime

class ProfileView(View):
    def dispatch(self, request, *args, **kwargs):
        super_dispatch = super(ProfileView, self).dispatch

        if not self._can_get_profile():
            return super_dispatch(request, *args, **kwargs)

        filename = self._make_profile_path()
        prof = cProfile.Profile()
        try:
            return prof.runcall(super_dispatch, request, *args, **kwargs)
        finally:
            prof.dump_stats(filename)

    def _get_my_class_name(self):
        return '.'.join([self.__module__, self.__class__.__name__])

    def _can_get_profile(self):
        if not hasattr(settings, 'GTOOLKIT_PROFILE_VIEWS'):
            return False

        if self._get_my_class_name() not in settings.GTOOLKIT_PROFILE_VIEWS:
            return False

        if hasattr(settings, 'GTOOLKIT_PROFILE_HOSTS'):
            if socket.gethostname() not in settings.GTOOLKIT_PROFILE_HOSTS:
                return False

        return True

    def _make_profile_path(self):
        root_path = getattr(settings, 'GTOOLKIT_PROFILE_PATH',
                            os.path.join('/', 'tmp', 'profile'))
        full_path = os.path.join(root_path, self._get_my_class_name())

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        return os.path.join(full_path, str(datetime.now_epoch()) + '.profile')


def timeit(fun=None, stdout=None):
    """
    簡易的な関数の時間計測に使用する.
    本気の計測は, ProfileView を使用すること.

    .. code-block:: python

        class Command(BaseCommand):
            @timeit # 経過時間が標準出力に出力
            def handle(self, *args, **options):
                self._process()

            import sys
            @timeit(stdout=sys.stderr) # 経過時間が標準エラーに出力
            def _process(self):
                pass
    """
    if stdout is None:
        stdout = sys.stdout

    def _timeit(f):
        @wraps(f)
        def _inner(*args, **kwargs):
            ts = time.time()
            result = f(*args, **kwargs)
            te = time.time()
            stdout.write(u'func:{} args:[{}, {}] took: {} sec\n' \
                .format(f.__name__, args, kwargs, te-ts))
            stdout.flush()
            return result

        return _inner

    return _timeit(fun) if fun else _timeit


class _StopWatchBase(object):
    def __init__(self, message=None):
        self._message = message

    def start(self):
        self._ts = time.time()

    def stop(self):
        te = time.time()
        self.elapsed = te - self._ts
        return self.elapsed

    def _get_caller(self):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        return {'file': calframe[2][1],
                'line': calframe[2][2],
                'function': calframe[2][3],}

    def __enter__(self):
        self.start()
        self.caller = self._get_caller()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return exc_type is None

    def _to_dict(self):
        dic = {'elapsed': self.elapsed}

        if self._message:
            dic['message'] = self._message

        if hasattr(self, 'caller'):
            dic['caller'] = self.caller

        return dic

    def __repr__(self):
        return repr(self._to_dict())


class StopWatch(_StopWatchBase):
    """
    処理時間を計測する StopWatch.
    メリットは ProfileView より処理に負荷を掛けない事.
    デメリットは, 使用時にコードを埋め込む手間が必要な事.

    処理に 3 秒以上掛かった場合にのみ出力する例は, 下記の通り.

    .. code-block:: python

        import logging
        from gtoolkit.profile from StopWatch

        class SpamView(HamView):
            def get(self, request, *args, **kwargs):
                with StopWatch(logger=logging.getLogger('spam'),
                               time_limit=3.0) as sw:
                    with sw.recording():
                        self._process1()

                    with sw.recording():
                        self._process2()
    """
    class _Record(_StopWatchBase):
        pass

    def recording(self, message=None):
        record = self._Record(message=message)
        self._records.append(record)
        return record

    def __init__(self, logger=None, message=None, time_limit=None):
        """
        :param object logger: Python 標準の Logger Object
        :param string message: ログを出力する際に付与する文字列
        :param float time_limit: ログを出力する最短の秒数
        """
        self._logger = logger
        self._message = message
        self._time_limit = time_limit

        self._records = []

    def stop(self):
        elapsed = super(StopWatch, self).stop()
        self._logging()
        return elapsed

    def _logging(self):
        if not self._logger:
            return

        if self._time_limit and self.elapsed < self._time_limit:
            return

        self._logger.warn(self._to_dict())

    def _to_dict(self):
        dic = super(StopWatch, self)._to_dict()
        dic['records'] = [record._to_dict() for record in self._records]
        return dic


class NullStopWatch(object):
    """
    StopWatch Object をオプションで受け取る際,
    このクラスのインスタンスを初期値として使用する事.

    .. code-block:: python

        def spam(stop_watch=None):
            if stop_watch is None:
                stop_watch = NullStopWatch()

            with stop_watch.recording():
                do_someting()
    """
    class _NullRecord(object):
        def __enter__(self):
            pass

        def __exit__(self, exc_type, exc_value, traceback):
            return exc_type is None

    def recording(self):
        return self._NullRecord()
