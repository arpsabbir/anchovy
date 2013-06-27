# -*- coding: utf-8 -*-


"""
10% 20% ... を表示するツール
バッチスクリプト用
"""

import datetime

class ProgressPrinter(object):
    
    """
    >>> from gsocial.log import Log
    >>> progress_printer = ProgressPrinter(1000)
    >>> progress_printer.set_print_method(Log.info)
    >>> for i in xrange(1000):
    ...    progress_printer.print_or_silent(i)

    # こんな感じに出力される
    [00:19:57]   0% complete.(     0/  1000)
    [00:19:57]  10% complete.(   100/  1000)
    [00:19:57]  20% complete.(   200/  1000)
    [00:19:57]  30% complete.(   300/  1000)
    [00:19:57]  40% complete.(   400/  1000)
    [00:19:57]  50% complete.(   500/  1000)
    [00:19:57]  60% complete.(   600/  1000)
    [00:19:57]  70% complete.(   700/  1000)
    [00:19:57]  80% complete.(   800/  1000)
    [00:19:57]  90% complete.(   900/  1000)
    """
    
    def print_method_default(self, msg):
        print(msg)
    
    def __init__(self, all_count):
        self.all_count = all_count
        self.latest_progress_percent = None
        self.print_method = self.print_method_default
    
    def set_print_method(self, func):
        self.print_method = func
    
    def print_initial_line(self):
        self.print_method(u'[%s] start. total_count=%d' % (
            datetime.datetime.now().strftime("%H:%M:%S"), self.all_count))
    
    def print_or_silent(self, current_count):
        current_count = min(current_count, self.all_count)
        current_progress_percent = int(float(current_count) / self.all_count *10) *10 #10%刻みの進捗
        if self.latest_progress_percent < current_progress_percent:
            self.print_method(u'[%s] % 3s%% complete.(% 6s/% 6s)' % (
                datetime.datetime.now().strftime("%H:%M:%S"),
                current_progress_percent, current_count, self.all_count))
            self.latest_progress_percent = current_progress_percent
