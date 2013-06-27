# -*- coding: utf-8 -*-

import urllib
import re

class Sure(object):
    def __init__(self, l):
        # データの格納
        split_result = re.split('<>', l)
        if len(split_result) != 2:
            self.dat = None
            self.title = None
            self.post_count = None

        self.dat = self.get_dat(split_result)
        self.title = self.get_title(split_result)
        self.post_count = self.get_post_count(split_result, self.title)

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
        return re.sub(r'\(\d+\)', '', split_result[1])

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

