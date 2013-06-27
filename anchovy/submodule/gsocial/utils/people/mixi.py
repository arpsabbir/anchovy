# -*- coding: utf-8 -*-
"""
mixi people api
"""
from base import PeopleBase


class PeopleMixi(PeopleBase):
    """
    PeopleAPIを使う（mixi用）

    プラットフォームからのレスポンス（JSON）のキーに関して
        greeとmixiは'entry'キー、mobageは'person'キーを利用する
    """
    pass
