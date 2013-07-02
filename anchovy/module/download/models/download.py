# -*- coding:utf-8 -*-
import urllib
import re
from module.download.constants import FILE_CHARACTER_CODE, FILE_OPEN_OPTION


class Download(object):
    lines = []

    def __init__(self, url_string):
        self.url = url_string
        self.lines = []

        # download
        f = self._download(url_string)

        for l in f.readlines():
            # デコード
            l = l.decode(FILE_CHARACTER_CODE, FILE_OPEN_OPTION)

            # 改行コードの削除
            l = re.sub(r'\n', '', l)
            self.lines.append(l)
        f.close()

    def _download(self, url_string):
        return urllib.urlopen(url_string)
