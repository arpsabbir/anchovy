# -*- coding: utf-8 -*-
"""
APIのテスト
"""
from optparse import make_option
import re
from django.conf import settings
from django.core.management.base import BaseCommand
from module.download.models.download import Download
from module.parser.res import Res


class Command(BaseCommand):
    """
    python manage.py sure_parser
    """
    option_list = BaseCommand.option_list + (
        make_option(
            '--url', action='store', dest='url', default=None,
            help=u'urlを入力',
            ),
        )


    def handle(self, *args, **options):
        url_string = options.get('url', None)

        str1 = u"既にその名前は使われています<>sage<>2013/06/29(土) 00:00:48.67 ID:uTg9hb2u<> 90000→10102コンボきたー <>"
        self._run(str1)

    def _run(self, str1):
        print "start"
        print u"str1:%s" % str1

        split_result = re.split('<>', str1)
        print split_result, len(split_result)

        # ct = 1
        # for m in split_result:
        #     print ct, m
        #     ct +=1

        r = Res(str1, 1)

        print r.post_name
        print r.post_mail
        print r.post_id
        print r.message













