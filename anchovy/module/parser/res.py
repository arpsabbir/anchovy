# -*- coding: utf-8 -*-

import urllib
import re
from urlparse import urljoin


class Res(object):
    """
    既にその名前は使われています<>sage<>2013/06/29(土) 00:00:48.67 ID:uTg9hb2u<> 90000→10102コンボきたー <>
    """

    def __init__(self, l, number, dat_url):
        # 投稿番号
        self.number = number

        # この投稿に対するレス番号
        self.ask = []

        self.dat_url = dat_url

        # データの格納
        split_result = re.split('<>', l)
        if len(split_result) != 5:
            self.post_name = None
            self.post_mail = None
            self.post_id = None
            self.message = None

        self.post_name = split_result[0]
        self.post_mail = split_result[1]
        self.post_id = split_result[2]
        self.message = split_result[3]
        self.reply = self._get_reply()

    def _get_reply(self):
        if self.message:
            m = re.search(r'>&gt;&gt;\d{1,3}', self.message)
            if m:
                reply = m.group(0)
                reply = re.sub(r'>&gt;&gt;', '', reply)
                try:
                    return int(reply)
                except ValueError:
                    return None
        return None

    def add_ask(self, number):
        self.ask.append(number)

    @property
    def ask_count(self):
        return len(self.ask)

    def show(self):
        print self.number
        print self.post_id
        print self.message
        print self.ask
        print self.ask_count


class ItaParser(object):
    def __init__(self, dat_download):
        count = 1
        self.res_dict = {}

        for l in dat_download.lines:
            try:
                r = Res(l, count, dat_download.url)
                self.res_dict[r.number] = r

                # 特定の書き込みにレスがあれば追加
                self._add_ask(r)


                # print r.number
                # print r.post_name
                # print r.post_mail
                # print r.post_id
                # print r.message

            except IndexError:
                print "==========================================="
                print "error!!!"
                print count
                print l
                print "==========================================="
                pass
            finally:
                count += 1

    def __iter__(self):
        return self

    def next(self):
        return self.res_dict

    def get(self, number):
        return self.res_dict.get(number)

    def set(self, number, r):
        self.res_dict[number] = r

    def _add_ask(self, r):
        """
        レスがあれば、対象の書き込みのaskを更新
        """

        if r and r.reply:
            self._update_ask(r.reply, r.number)

    def _update_ask(self, reply, number):
        """
        レスがあった書き込み番号を記録
        reply : 対象の書き込み番号
        number : レス元の書き込み番号
        """
        if 2 <= reply <= 980:
            r = self.get(reply)
            if r:
                r.add_ask(number)
                self.set(reply, r)
