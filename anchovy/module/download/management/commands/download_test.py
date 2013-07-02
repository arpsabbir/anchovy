# -*- coding: utf-8 -*-
"""
APIのテスト
"""
from optparse import make_option
import random
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from module.download.models.download import Download
from module.ita import Ita
from module.mecab.mecab_analysis import MeCabAnalysis
from module.mecab.mecab_wrapper import MeCabWrapper
from module.parser.res import ItaParser
from module.parser.sure import Sure


class Command(BaseCommand):
    """
    ff14 スレッドダウンロード
    python manage.py download_test --url="http://awabi.2ch.net/ogame/subject.txt"
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--url', action='store', dest='url', default=None,
            help=u'urlを入力',
            ),
        )


    def handle(self, *args, **options):
        url_string = options.get('url', None)
        self._run(url_string)

    def _run(self, url_string):
        print "start"
        print u"url_string:%s" % url_string

        # 一覧ダウンロード
        download = Download(url_string)
        sure_list = []


        keyword_list = []
        for l in download.lines:
            try:
                sure = Sure(l, url_string)
            except TypeError:
                continue

            if sure.post_count > 100:
                print sure.title
                sure_list.append(sure)

                # MeCab
                mecab_wrapper = MeCabWrapper(sure.title)
                keyword_list += mecab_wrapper.word_list


        # スレタイ一覧からキーワードを抽出
        anal = MeCabAnalysis(keyword_list)
        anal.show()
        unique_word_list = anal.unique_word_list

        # test
        # unique_word_list.remove("FF14")

        # キーワードにマッチするタイトル一覧の表示
        print "==========START SHOW MATCH SUBJECT=========="
        for sure in sure_list:
            title = sure.title

            for unique_word in unique_word_list:
                if unique_word.decode('utf-8') in title:
                    print title, unique_word
                    break

                # m = re.search(unique_word, title)
                # if m:
                #     print title, unique_word



        # スレダウンロード
        # for sure in sure_list:
        #     dat_download = Download(sure.dat_url)

        # dat ダウンロード
        sure = sure_list[5]
        print "dat_url:%s" % sure.dat_url
        dat_download = Download(sure.dat_url)

        res_factory = ItaParser(dat_download)

        for r in res_factory.next():
            r = res_factory.get(r)

            # レス多いコメントだけ表示
            if r.ask_count > 2:
                print "===================================="
                r.show()

                # レスも表示する
                for comment_number in r.ask:
                    r = res_factory.get(comment_number)
                    r.show()


    def _get_delimiter(self):
        """
        区切り文字を取得
        ランダムにして、カウントされないようにする
        """
        DELI = [
            "§",
            "¢",
            "£",
            "¨",
            "▼",
            "☆",
            "▲",
            "□",
            "◆",
            "▽",
            "○",
            "★",
            "◆",
            "◇",
            "▽",
            "■",
            "◎",
            "△",
            "●",
        ]

        return random.choice(DELI)

