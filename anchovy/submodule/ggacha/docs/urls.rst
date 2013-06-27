============
URL を決める
============

モデルクラス, 課金クラス, ガチャ処理クラスの準備ができた後,
URL を決めて urls.py に内容を追加して行く.
具体的には, ガチャ毎に下記の様な URL が必要となる.

無料(ポイント)ガチャ:

- ガチャを行う URL
- FLASH を表示する URL
- 結果を表示する URL

有料(GREEコイン)ガチャ:

- ガチャを行う URL
- GREE のコールバックを受ける URL
- FLASH を表示する URL
- 結果を表示する URL

URL 一つにつき, 一つの View クラスが対応するため,
もし幻獣姫の桃源郷ガチャ, 黄金郷ガチャ, 6連黄金郷ガチャを作るならば,
urls.py の import は次の様になる.
ただし, この時点では, まだ View クラスは存在していないため, コンパイルエラーとなる.

.. code-block:: python

    from module.gacha.xanadu.views import (XanaduView,
                                           XanaduFinishView,
                                           XanaduResultView)

    from module.gacha.golden.views import (GoldenView,
                                           GoldenCallbackView,
                                           GoldenFinishView,
                                           PaymentResultView)

    from module.gacha.golden6.views import (Golden6View,
                                            Golden6CallbackView,
                                            Golden6FinishView,
                                            Payment6ResultView)


これを, urlpatterns に設定して行く.


.. code-block:: python

    from django.conf.urls.defaults import patterns, url

    urlpatterns = patterns('',
        # 桃源郷
        url(r'xanadu/$',
            XanaduView.as_view(),
            name='mobile_gacha_zanadu'),
        url(r'xanadu/finish/$',
            XanaduFinishView.as_view(),
            name='mobile_gacha_zanadu_finish'),
        url(r'xanadu/result/$',
            XanaduResultView.as_view(),
            name='mobile_gacha_zanadu_result'),

        # 黄金郷
        url(r'golden/$',
            GoldenView.as_view(),
            name='mobile_gacha_golden'),
        url(r'golden/callback/$',
            GoldenCallbackView.as_view(),
            name='mobile_gacha_golden_callback'),
        url(r'golden/finish/$',
            GoldenFinishView.as_view(),
            name='mobile_gacha_golden_finish'),
        url(r'golden/result/$',
            GoldenResultView.as_view(),
            name='mobile_gacha_golden_result'),

        # 6連 黄金郷 
        url(r'golden6/$',
            Golden6View.as_view(),
            name='mobile_gacha_golden6'),
        url(r'golden6/callback/$',
            Golden6CallbackView.as_view(),
            name='mobile_gacha_golden6_callback'),
        url(r'golden6/finish/(?P<count>\d)/$',
            Golden6FinishView.as_view(),
            name='mobile_gacha_golden6_finish'),
        url(r'golden6/result/$',
            Golden6ResultView.as_view(),
            name='mobile_gacha_golden6_result'),
    )


6連等の連続ガチャの場合, どこかで FLASH を分割する必要があるため, URL に表示回数を含めている.
