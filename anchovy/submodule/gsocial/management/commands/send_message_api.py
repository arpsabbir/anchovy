# -*- coding: utf-8 -*-

"""
テスト中!
send_message_api のスレッドセーフ版
テスト結果が良好なら gsocial　に入れる
(その場合、gsocial.management.tools.threadpool も一緒に消す)

メッセージAPIを全osuserに送信するスクリプト

使い方: ./manage.py send_message_api --title="告知のテスト" --body="大変失礼いたしました。本メッセージはテスト目的で送信されたものです。" --send

"""

import datetime
import sys
import os
from optparse import make_option
from Queue import Queue
from threading import Thread

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils.encoding import smart_str
from django.core.urlresolvers import reverse
from gsocial.utils.message import Message

from gsocial.models import OpenSocialUser
from gsocial.management.tools.progress_printer import ProgressPrinter

# 同時送信人数最大
MAX_TREADS = 30

# 同時送信人数最大
MAX_SEND_COUNT = 20


def get_callback_url(url_name=None):
    """
    コールバックURLを指定
    """
    if not url_name:
        url_name = 'root_home'
    return reverse(url_name)


class SendMessageWorker(Thread):
    """
    メッセージAPI送信ワーカースレッド
    キューから取って実行、を繰り返す
    """
    def __init__(self, q, title_msg, body_msg, callback_url, progress_printer):
        self.q = q # (ユーザーIDリスト、プログレス) が詰まってる(詰められる)キュー
        self.title_msg = title_msg
        self.body_msg = body_msg
        self.callback_url = callback_url
        self.progress_printer = progress_printer
        super(SendMessageWorker, self).__init__()

    def run(self):
        while True:
            osuser_ids, progress = self.q.get()
            message_api = Message(None)
            try:
                message_api.sends(None, osuser_ids, self.title_msg, self.body_msg, self.callback_url)
            except Exception as e:
                # エラー処理どうしよう。raiseする?
                print '{}: {}'.format(e.__class__.__name__, e)
            finally:
                self.progress_printer.print_or_silent(progress)
                self.q.task_done()


def send_message_api_shard_osuser(title, body, logging_method=lambda x: None, only_shard=None, url_name=None):
    """
    osuserを全員分ループし、メッセージAPIを出していく
    """
    all_count = OpenSocialUser.objects.all_partition_count()
    logging_method(u'[%s] start. all_count=%s ' % (
        datetime.datetime.now().strftime("%H:%M:%S"), all_count))
    callback_url = get_callback_url(url_name)

    # 全シャードをループしてメッセージを送信
    for shard in range(settings.HORIZONTAL_PARTITIONING_PARTITION_NUMBER):
        if only_shard is not None: # only_shard が指定されている場合はそのシャードのみ
            if not shard == int(only_shard):
                continue
        db_name = settings.HORIZONTAL_PARTITIONING_DB_NAME_FORMAT % shard
        logging_method(u'processing shard %s...' % db_name)
        shard_count = OpenSocialUser.objects.using(db_name).all().count()

        q = Queue()

        # プログレスプリンタを用意する
        progress = 0
        progress_printer = ProgressPrinter(shard_count)
        progress_printer.set_print_method(logging_method)
        progress_printer.print_initial_line()

        # ワーカーを用意する
        for i in range(MAX_TREADS):
            t = SendMessageWorker(q, title, body,
                callback_url, progress_printer)
            t.setDaemon(True)
            t.start()

        # user_id, progress をキューにつめていく
        while True:
            userid_list = OpenSocialUser.objects.using(db_name).values_list(
                'userid', flat=True).order_by('userid')[progress:progress + MAX_SEND_COUNT]
            if not userid_list:
                break
            progress += MAX_SEND_COUNT
            q.put((list(userid_list), progress))
        q.join() #終わるまで待つ
        logging_method(u'shard %s done.' % db_name)

    logging_method(u'finished.')


def send_message_api_listed_osuser(title, body, user_id_list, logging_method=lambda x: None, url_name=None):
    """
    リストされたユーザーにメッセージAPIを送信
    """
    all_count = len(user_id_list)
    callback_url = get_callback_url(url_name)

    q = Queue()

    # プログレスプリンタを用意する
    progress_printer = ProgressPrinter(len(user_id_list))
    progress_printer.set_print_method(logging_method)
    progress_printer.print_initial_line()

    # ワーカーを用意する
    for i in range(MAX_TREADS):
        t = SendMessageWorker(q, title, body,
            callback_url, progress_printer)
        t.setDaemon(True)
        t.start()

    for i in xrange(0, all_count, MAX_SEND_COUNT):
        userid_list = user_id_list[i:i + MAX_SEND_COUNT] #20人づつ持ってくる
        q.put((list(userid_list), i + MAX_SEND_COUNT))
    q.join() #終わるまで待つ
    logging_method(u'finished.')


class Command(BaseCommand):
    help = u'''全osuserに対してメッセージAPIを送信します'''

    option_list = BaseCommand.option_list + (
        make_option('--title',
            action='store',
            dest='title',
            help=u'メッセージの件名'),
        make_option('--body',
            action='store',
            dest='body',
            help=u'メッセージの本文'),
        make_option('--only',
            action='store',
            dest='only',
            metavar="USERID",
            help=u'このUSERIDのみにメッセージを送信します。テスト用。'),
        make_option('--shard',
            action='store',
            dest='shard',
            help=u'このshardのユーザーにのみ送信します(数字)。'),
        make_option('--user-id-file',
            action='store',
            dest='user_id_file',
            metavar="USER_ID_FILE",
            help=u'改行区切りのユーザーIDのファイル。指定されたユーザーのみに送信します。'),
        make_option('--send',
            action='store_true',
            dest='send_execute',
            default=False,
            help=u'実際に送信します'),
#        make_option('--verbose',
#            action='store_true',
#            dest='verbose',
#            default=False,
#            help=u'ログ出力の冗長化'),
        make_option('--url-name',
            action='store',
            dest='url_name',
            help=u'遷移先URL名を指定します。'),
        #verbosityってのも使えるけどこれでいいか
        )

    def echo(self, message):
        self.stdout.write(smart_str(message, errors='ignore'))
        self.stdout.write('\n')
        self.stdout.flush()

    def error(self, message):
        raise CommandError(smart_str(message, errors='ignore'))

    def handle(self, *args, **options):
        title = options.get('title', None)
        body = options.get('body', None)
        shard = options.get('shard', None)

        # スクリプトの実行状態によってはクォーテーションで囲われてくる場合があるので除去
        if title:
            title = title.strip('''"' ''')
        if body:
            body = body.strip('''"' ''')

        if not title:
            self.print_help(sys.argv[0], sys.argv[1])
            return self.error(u'引数 --title= で件名を指定してください')
        if isinstance(title, str):
            title = title.decode('utf-8', 'ignore')
        self.echo(u'Title: %s' % title)

        if not body:
            self.print_help(sys.argv[0], sys.argv[1])
            return self.error(u'引数 --body= で本文を指定してください')
        if isinstance(body, str):
            body = body.decode('utf-8', 'ignore')
        self.echo(u'Body: %s' % body)

        user_id_list = None
        user_id_file = options.get('user_id_file', None)
        if user_id_file:
            if os.path.exists(user_id_file):
                user_id_list = open(user_id_file, 'r').read().splitlines()
                user_id_list = filter(lambda x: x, user_id_list)
            else:
                return self.error(u'user-id-fileが存在しません。(%s)' % user_id_file)

        only_osuser_id = options.get('only', None)
        if only_osuser_id:
            user_id_list = [only_osuser_id, ]

        #verbose = options.get('verbose', False)
        url_name = options.get('url_name')

        if options.get('send_execute', False):
            if user_id_list:
                send_message_api_listed_osuser(title, body, user_id_list,
                    logging_method=self.echo, url_name=url_name)
            elif shard:
                send_message_api_shard_osuser(title, body,
                    logging_method=self.echo, only_shard=shard, url_name=url_name)
            else:
                send_message_api_shard_osuser(title, body,
                    logging_method=self.echo, url_name=url_name)
        else:
            self.echo(u'--send オプションが指定されていないので、メッセージを出さずに終了しました。')
