# -*- coding: utf-8 -*-
"""
APIのテスト
"""
from optparse import make_option
from django.conf import settings
from django.core.management.base import BaseCommand
from module.download.models.download import Download
from module.sure.sure import Sure


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

        download = Download(url_string)

        for l in download.lines:
            sure = Sure(l)
            if sure.post_count > 800:
                print sure.title


