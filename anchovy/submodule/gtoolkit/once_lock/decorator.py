# -*- coding:utf-8 -*-
import time
import hashlib
from functools import wraps

from django.core.cache import cache


def lock_and_execute_view_func(view_func, self, request, view_args, view_kwargs, cache_timeout=15, key_prefix=None):

    # ロックキー、レスポンスキャッシュキーの生成　
    if key_prefix:
        path = key_prefix
    else:
        params = []
        if request.method == 'POST':
            for param in request.POST:
                params.append('&%s=%s' % (param, request.POST[param]))
        param = ''.join(params).encode('utf-8')
        path = request.path + hashlib.md5(param).hexdigest()

    lockkey = 'Lockkey::OnceLock::%s::%s' % (path, str(self.os_user.userid))
    reskey = 'Reskey::OnceLockRes::%s::%s' % (path, str(self.os_user.userid))

    # cache_timeoutが0の場合はロックを解除するだけ
    if cache_timeout == 0:
        cache.delete(lockkey)
        cache.delete(reskey)
        res = view_func(self, request, *view_args, **view_kwargs)
        if hasattr(res, 'render'):
            # HttpResponseRedirectなどrenderを持たないもの用
            res.render()
        return res

    cache_res = cache.get(reskey, None)
    if cache_res:
        return cache_res

    # ロックチェック
    lock = cache.get(lockkey, None)
    if lock:
        for i in xrange(10000):
            #sleep(10ミリ秒指定)
            time.sleep(0.1)
            # キャッシュにレスポンスが入るまで待つ
            cache_res = cache.get(reskey, None)
            if cache_res:
                return cache_res

    # ロック取得
    cache.set(lockkey, 1)

    # 該当viewを実行
    try:
        res = view_func(self, request, *view_args, **view_kwargs)
        if hasattr(res, 'render'):
            res.render()
    except:
        # ロックを解除
        cache.delete(lockkey)
        raise

    # 結果を一時的に保存
    cache.set(reskey, res, cache_timeout)
    # ロックを解除
    cache.delete(lockkey)
    return res


def once_lock(*args, **kwargs):
    """
    一度だけしか実行されないようにロックする
    結果が出ている場合はキャッシュから取得する

    ex)
    @once_lock
    def view_func():
        pass

    @once_lock(cache_timeout=15, key_prefix='hoge')
    def view_func():
        pass

    Arguments:
    - `cache_timeout`:ロック時間(秒) ※ 0を渡した場合はロックを解除してview実行
    - `key_prefix`: 指定した場合のキャッシュ単位       > key_prefix + OSUSER_ID
                    指定しなかった場合のキャッシュ単位 > URL + POSTパラメータ + OSUSER_ID
    """
    cache_timeout = kwargs.pop('cache_timeout', None)
    key_prefix = kwargs.pop('key_prefix', None)
    assert not kwargs, "Keyword argument accepted is key_prefix or cache_timeout"
    if key_prefix is None and cache_timeout is None:
        view_func = args[0]

        @wraps(view_func)
        def decorate(self, request, *v_args, **v_kwargs):
            return lock_and_execute_view_func(view_func, self, request, v_args, v_kwargs)
        return decorate
    else:
        kwargs_for_lock = {}
        if not cache_timeout is None:
            kwargs_for_lock['cache_timeout'] = cache_timeout
        if not key_prefix is None:
            kwargs_for_lock['key_prefix'] = key_prefix

        def _internal_params(view_func):
            @wraps(view_func)
            def decorate(self, request, *v_args, **v_kwargs):
                return lock_and_execute_view_func(view_func, self, request, v_args, v_kwargs, **kwargs_for_lock)
            return decorate
        return _internal_params

