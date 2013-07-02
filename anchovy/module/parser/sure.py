# -*- coding: utf-8 -*-

import urllib
import re
from urlparse import urljoin
from module.mecab.ng_word import NGBase


class Sure(object):
    """
    subject ファイル
    http://news22.2ch.net/newsplus/subject.txt

    dat ファイル
    http://news22.2ch.net/newsplus/dat/1185716060.dat
    """

    def __init__(self, l, subject_url):
        self.subject_url = subject_url

        # データの格納
        split_result = re.split('<>', l)
        if len(split_result) != 2:
            self.dat = None
            self.title = None
            self.post_count = None

        self.dat = self.get_dat(split_result)
        self.title = self.get_title(split_result)
        self.post_count = self.get_post_count(split_result, self.title)

    @property
    def dat_url(self):
        _dat_path = 'dat/' + self.dat + '.dat'
        return urljoin(self.subject_url, _dat_path)

    def get_dat(self, split_result):
        """
        u'1362274743.dat<>【新生FF14】βテスター専用スレ　Part144 (259)'
        ↓抽出

        1362274743
        """
        return re.sub(r'\.dat', '', split_result[0])

    def get_title(self, split_result):
        """
        u'1362274743.dat<>【新生FF14】βテスター専用スレ　Part144 (259)'
        ↓抽出

        【新生FF14】βテスター専用スレ　Part144
        """
        title = re.sub(r'\(\d+\)', '', split_result[1])

        if NGBase.check(title):
            raise TypeError
        return title



    def get_post_count(self, split_result, title):
        """
        u'1362274743.dat<>【新生FF14】βテスター専用スレ　Part144 (259)'
        ↓抽出

        259
        """
        try:
            post_count = re.sub(title, '', split_result[1])
            post_count = re.search(r'\d+', post_count).group(0)
            post_count = int(post_count)
        except:
            return None

        return post_count

