# -*- coding: utf-8 -*-


class ResponseError(Exception):
    """
    Raise errors when problems arise at connecting with the platforms.
    eg. raise self.ResponseError('blacklist2')

    SNSとの通信が発生した時とかに投げる例外
    例: raise self.ResponseError('blacklist2')
    """
    method_name = ''  # メソッド名を入れておく
    section = ''  # エラー発生箇所を入れておく
    response_data = None  # レスポンスデータを入れる、ダンプして中身見る用

    def __init__(self, method_name='', section='', response_data=None):
        self.method_name = method_name
        self.section = section
        self.response_data = response_data

    def __str__(self):
        return self.dump()

    def dump(self):
        """
        Dump the error information and return it.
        エラー情報をダンプして返す
        """
        return '%s: %s: %s' % (self.method_name, self.section,
                               repr(self.response_data))


class SessionError(Exception):
    """
    保存してあるセッション情報に問題があったら送出されるエラー
    """
    pass