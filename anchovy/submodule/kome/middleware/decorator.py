#coding: utf-8

from functools import wraps
from kome.middleware._log import log

class _LogDecorator:
    def __getattr__(self, name):
        def f(*args, **kwargs):
            def f2(func):
                def f3(*args2, **kwargs2):
                    inst = log()
                    logfunc = getattr(inst.__class__, name, None)
                    if logfunc is None:
                        logfunc_ = getattr(inst.__class__, '__getattr__')(inst, name)
                    else:
                        logfunc_ = lambda *args, **kwargs: logfunc(inst, *args, **kwargs)
                    with logfunc_(*args, **kwargs):
                        return func(*args2, **kwargs2)
                return f3
            return f2
        return f

deco = _LogDecorator()

def conductor_log(location_type):
    u'''
    導線ログ出力用デコレータ
    出力されるログは"log().view_page"

    decorater側で使用する引数
     location_type -- GACHA等のページの概要(view_pageの引数と同様)

    HTML(GET)側で使用する引数
     view_type -- ページ内のタイプ
     select_id -- 導線の区別を行う番号
    '''
    def decorate(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            url = request.path
            view_type = request.GET.get('view_type', 'None')
            select_id = request.GET.get('select_id', 'None')
            with log().view_page(location_type=location_type, url=url, view_type=view_type, select_id=select_id):
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorate
