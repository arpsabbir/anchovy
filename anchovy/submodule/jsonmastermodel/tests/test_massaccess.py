# -*- coding: utf-8 -*-
"""
大量スレッドからのアクセス

MockLargeModel.quick_filter などで、インスタンスのコピーを返すべきか?

10000処理を100スレッド同時にまわして、以下のような結果になった。

インスタンスを使いまわす場合: 4眇

使いまわしてるインスタンスのidを使って新たにインスタンスを作り、返す場合: 20眇
            return [cls.get(i.id) for i in out_list]

使いまわしてるインスタンスのシャローコピーを返す場合: 30眇
            return [copy.copy(i) for i in out_list]

使いまわしてるインスタンスのディープコピーを返す場合: 100眇
            return [copy.deepcopy(i) for i in out_list]


"""
from __future__ import unicode_literals
from Queue import Queue

import sys
import logging
import threading
import unittest
from gtoolkit.time.elapsed_time_watch import ElapsedTimeWatch

from .models import MockLargeModel


class Worker(threading.Thread):

    def __init__(self, q):
        self.q = q
        super(Worker, self).__init__()

    def run(self):
        # i = MockLargeModel.get(5000)
        # assert i.category == 'category-0'
        # self.semaphore.aquire()
        while True:
            rid = self.q.get()
            #i = MockLargeModel.get(5000)
            # logging.debug('id: {}, {}, {}'.format(
            #     id(MockLargeModel),
            #     id(MockLargeModel.objects._parsed_master_data),
            #     id(i)))
            #assert i.category
            #assert i.value
            #assert i.id

            i = MockLargeModel.quick_filter(category='category-5')[0]
            #logging.debug('id: {}, {}, {}'.format(
            #   id(MockLargeModel),
            #   id(MockLargeModel.objects._parsed_master_data),
            #   id(i)))
            assert i.category
            assert i.value
            assert i.id

            self.q.task_done()


class MassAccessTest(unittest.TestCase):

    def test_mass_access(self):
        """値の取得のテスト"""
        #s = threading.Semaphore
        #return

        try:
            MockLargeModel.get(1)
        except IOError as e:
            print >> sys.stderr, \
                'テストフィクスチャが作られていません'
            print >> sys.stderr, \
                '$ ./create_testfixture.py > jsonmastermodel-testfixture-large.json'
            print >> sys.stderr, \
                'を実行してください。(git ignored)'
            return

        q = Queue()
        etw = ElapsedTimeWatch()

        for i in range(100):
            t = Worker(q)
            t.setDaemon(True)
            t.start()
        etw.logging_ms('create workers')
        for i in xrange(1, 1000):
            q.put(i)

        q.join()
        etw.logging_ms('task done')
        etw.write_debug_log()