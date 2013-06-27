# -*- coding: utf-8 -*-
from gtoolkit.cache.memoize.function import clear_cache as f_clear
from gtoolkit.cache.memoize.query import clear_cache as q_clear

class MemoizePerRequestMiddleware(object):
    """
    リクエスト毎に関数をメモ化するため,
    このミドルウェアでリクエスト毎にキャッシュ先のインスタンスを作成する
    """
    def process_request(self, request):
        f_clear()
        q_clear()
