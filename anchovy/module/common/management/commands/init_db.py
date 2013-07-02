# -*- coding: utf-8 -*-
"""
init_db.shの中で呼ばれる。
syncdb, migrate, load dataを行う
"""
import os
import commands
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import gdio


class Command(BaseCommand):
    def handle(self, *args, **options):

        # DEBUG環境のみ許可
        if settings.DEBUG:
            pass
        elif settings.OPENSOCIAL_DEBUG:
            pass
        elif settings.OPENSOCIAL_SANDBOX:
            pass
        else:
            raise CommandError('Cannot execute in production servers.')

        # Redisを初期化
        hr()
        print('---- redis flush start.')
        for redis_name, redis_setting in settings.REDIS_DATABASES.items():
            redis_flush(redis_name, redis_setting)

        print('---- redis flush done.')

        # syncdbでsouth管理以外のテーブル作成
        hr()
        print('---- syncdb command start.')
        # defaultを最初にやらないとcontent_typeエラーがでる
        syncdb('default')
        for database_name in settings.DATABASES.keys():
            if database_name == 'default':
                continue
            syncdb(database_name)

        print('---- syncdb command done.')

        # south管理のテーブル作成
        hr()
        execute('./manage.py migrate_db --settings={SETTINGS}'.format(
            SETTINGS=settings.SETTINGS_MODULE), nowait=True)

        # 初期データ読み込み
        gdio.init()
        hr()
        print('---- load_db command start.')
        execute('./manage.py load_db all --settings={SETTINGS}'.format(
            SETTINGS=settings.SETTINGS_MODULE), nowait=True)
        print('---- load_db command done.')

        hr()
        print('---- clean_memcached command start.')
        execute('./manage.py clean_memcached --settings={SETTINGS}'.format(
            SETTINGS=settings.SETTINGS_MODULE), nowait=True)
        print('---- clean_memcached command done.')
        hr()


def redis_flush(redis_name, redis_setting):
    command = 'redis-cli -p {PORT} -h {HOST} -n {DB} {COMMAND}'.format(
        PORT=redis_setting['PORT'],
        HOST=redis_setting['HOST'],
        DB=redis_setting['DB'],
        COMMAND='flushdb'
    )
    print 'redis[{}]:  {}'.format(redis_name, command)
    execute(command)


def syncdb(database_name):
    command = './manage.py syncdb --noinput --database={DATABASE_NAME} --settings={SETTINGS}'.format(
        DATABASE_NAME=database_name,
        SETTINGS=settings.SETTINGS_MODULE
    )
    print('command: %s' % command)
    execute(command)


def execute(cmd, nowait=False):
    if nowait:
        os.system(cmd)
    else:
        _status, output = commands.getstatusoutput(cmd)
        print(output)


def hr(line='-' * 50):
    print(line)
