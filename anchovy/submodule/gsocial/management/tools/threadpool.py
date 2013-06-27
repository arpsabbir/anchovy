#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
シンプルなスレッドプール
    threadpool = ThreadPool(3)
    threadpool.add_job(メソッド)
    threadpool.start()
"""

import time
import threading

class Worker(threading.Thread):
    def set_job(self, job):
        self.job = job
    def set_method_at_start_end(self, ms, me):
        self.method_at_start = ms
        self.method_at_end = me
    def run(self):
        self.method_at_start()
        self.job()
        self.method_at_end()

class ThreadPool(object):
    
    def __init__(self, capacity):
        self.current_capacity = 0 # セマフォ
        self.max_capacity = capacity
        self.job_pool = []

    def add_job(self, job):
        self.job_pool.append(job)

    def increase_capacity(self):
        self.current_capacity += 1

    def decrease_capacity(self):
        self.current_capacity -= 1

    def wait(self):
        while self.current_capacity >= self.max_capacity:
            time.sleep(0.1)

    def wait_for_zero(self):
        while self.current_capacity:
            time.sleep(0.1)

    def start(self):
        jobs = self.job_pool
        for job in jobs:
            w = Worker()
            w.set_job(job)
            w.set_method_at_start_end(self.increase_capacity, self.decrease_capacity)
            w.start()
            self.wait()
        self.wait_for_zero()

def test():
    
    class Tester(object):
        def __init__(self, name, log):
            self.name = name
            self.log = log
        def testwait(self):
            self.log.append('%s: testwait start.' % self.name)
            for i in range(1,4):
                time.sleep(0.3)
                self.log.append('%s: loop%s' % (self.name, i,))
    
    threadpool = ThreadPool(3)
    log = []
    testers = [ Tester(i, log) for i in xrange(10) ]
    for tester in testers:
        threadpool.add_job(tester.testwait)
    threadpool.start()
    print('end')
    print('\n'.join(log))

if __name__ == "__main__":
    test()

