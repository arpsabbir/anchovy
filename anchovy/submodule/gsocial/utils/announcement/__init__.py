# -*- coding: utf-8 -*-
"""
Announcement API
"""

from gsocial.utils.announcement.gree import AnnouncementGree

class MetaAnnouncementAPI(type):
    def __new__(mcs, name, bases, attrs):
        from gsocial.setting import GREE
        from gsocial.set_container import Container
        if Container().name == GREE:
            bases = (AnnouncementGree,)
        return type.__new__(mcs, name, bases, attrs)

class AnnouncementAPI(object):
    """
    プラットフォームを考慮したアナウンスメントAPI
    """
    __metaclass__ = MetaAnnouncementAPI
