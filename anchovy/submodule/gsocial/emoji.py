# -*- coding: utf-8 -*-
"""
絵文字処理
"""
import re
from gsocial.log import Log


class Emoji(object):

    def __init__(self):
        """
        __init__
        """
        # encode_emoji、decode_emojiで使う
        self.emoji_re = None
        # decode_emojiで使う
        self.emoji_decode_re = None

    def encode_emoji(self, text):
        """
        絵文字をエンコードして返す
        GREEのInspectionAPI、モバゲーのTextDataAPI用
        \ue000 -> &#xe000 に変換

        引数
         text

        返り値
         エンコードした絵文字を返す
        """
        if self.emoji_re is None:
            self.emoji_re = re.compile(u'[\ue000-\uf0fc]')

        Log.debug('encode_emoji before: %r' % text)

        def emoji_open(m):
            """
            emoji_open
            """
            return '&#x%x' % ord(m.group(0))

        encoded = self.emoji_re.sub(emoji_open, text)
        Log.debug('encode_emoji after: %r' % encoded)
        return encoded

    def decode_emoji(self, text):
        """
        絵文字をデコードして返す
        GREEのInspectionAPI、モバゲーのTextDataAPI用
        &#xe000 -> \ue000に変換
        絵文字じゃない &#xXXXX は空文字にする

        引数
         text

        返り値
         デコードした絵文字を返す
        """
        if self.emoji_re is None:
            self.emoji_re = re.compile(u'[\ue000-\uf0fc]')
        if self.emoji_decode_re is None:
            self.emoji_decode_re = re.compile(r'&#x(\w{4})')

        Log.debug('decode_emoji before: %r' % text)

        def emoji_close(m):
            """
            emoji_close
            """
            c = unichr(int(m.group(1), 16))
            if self.emoji_re.search(c):
                return c
            else:
                return ''

        decoded = self.emoji_decode_re.sub(emoji_close, text)
        Log.debug('decode_emoji after: %r' % decoded)
        return decoded
