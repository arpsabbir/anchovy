# -*- coding: utf-8 -*-
"""
テスト用の一時対応

Django Test で Fixture をロードする場合,
django.db.transaction の関数が nop 関数に置き換わる事で,
Fixture が確実に rollback される事を保証しているため,
本モジュールが提供するトランザクション関連の API と相性が悪い.
(テストケース全体がトランザクションの中)

よって, Django Test で使用する場合は, トランザクションを無効にする必要がある.
トランザクションを無効にする例は次の通り.

.. code-block:: python

    import horizontalpartitioning

    class SpamTest(TestCase):
        def setUp(self):
            horizontalpartitioning.adhoc.ON_TEST = True

        def tearDown(self):
            horizontalpartitioning.adhoc.ON_TEST = False
"""
ON_TEST = False
