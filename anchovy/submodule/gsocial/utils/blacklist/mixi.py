# -*- coding: utf-8 *-
"""
mixi black list api
"""
from base import BlacklistBase

class BlacklistMixi(BlacklistBase):
    """
    Ignorelist APIを使う(mixi用）
    未リファクタ
    """
    def platform(self):
        """
        return platform name
        """
        return 'mixi'

