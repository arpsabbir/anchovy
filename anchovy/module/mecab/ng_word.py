# -*- coding: utf-8 -*-
import re

# 集計対象外
NG_WORD = [
    u"晒",
    u"キチガイ",
    u"キ○ガイ",
]

# 除外ワード
REMOVE_WORD = [
    u"スレ",
    u"目",
    u"part",
    u"Part",
    u"PART",
]


class NGBase(object):
    WORD_LIST = NG_WORD

    @classmethod
    def check(cls, text):
        """
        マッチしたらTrue
        """
        for _ng in cls.WORD_LIST:
            m = re.search(_ng, text)
            if m:
                return True
        return False

    @classmethod
    def remove(cls, text):
        """
        textからNGワードを除外して返却
        """
        for _ng_word in cls.WORD_LIST:
            text = re.sub(r'%s' % _ng_word, '', text)
        return text

class NGWord(NGBase):
    WORD_LIST = NG_WORD

class RemoveWord(NGBase):
    WORD_LIST = REMOVE_WORD
