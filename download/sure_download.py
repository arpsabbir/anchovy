# -*- coding: utf-8 -*-

import urllib
from models.sure import Sure
"""
スレをダウンロードしてパースする
"""


url = "http://awabi.2ch.net/ogame/subject.txt"
f = urllib.urlopen(url)

sure_list = []

for file_obj in f.readlines():
    sure_list.append(Sure(file_obj))

f.close()

