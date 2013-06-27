# -*- coding:utf-8 -*-
"""
Log Format
Log Output
"""
import logging

class Log(object):
    """
    Log output class
    
    ログ出力クラス
    """
    _logger = logging.getLogger('gsocial')

    @classmethod
    def _get_logging_res(cls, msg, obj=None):
        """
        Format the log data and return it.
        出力用にフォーマットして返す
        """
        if obj is None:
            return msg
        format_msg = '"%s", %s'
        return format_msg % (msg, obj)

    @classmethod
    def debug(cls, msg, obj=None):
        """
        For debug.
        debug用
        """
        cls._logger.debug(cls._get_logging_res(msg, obj))

    @classmethod
    def info(cls, msg, obj=None):
        """
        For info.
        info用
        """
        cls._logger.info(cls._get_logging_res(msg, obj))

    @classmethod
    def error(cls, msg, obj=None):
        """
        For error.
        error用
        """
        cls._logger.error(cls._get_logging_res(msg, obj))

    @classmethod
    def warn(cls, msg, obj=None):
        """
        For warning.
        warning用
        """
        cls._logger.warn(cls._get_logging_res(msg, obj))
