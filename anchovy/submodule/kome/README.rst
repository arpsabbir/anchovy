kome
=========

kome は、ユーザの行動ログを出力するためのライブラリです。

このライブラリは G-SAF 仕様に準拠したフォーマットで出力します。

クラス構成
--------

大きく分けて、Sender, ActionLog, DerivedLog の３つがあります。

Sender は、ログ出力の送信先を決めるためのクラスです。
例えば syslog に送信したり、fluentd に送信したり、あるいは標準出力に送信したりと、Sender に指定するプラグインを切り替えることで、様々な方法でログを送信することができます。

ActionLog は、アクションログを出力するためのクラスです。
ユーザの行動を、このクラスを使って出力します。

DerivedLog は、派生ログを出力するためのクラスです。
ActionLog でアクションログを出力した結果、そのアクションに関連付けられた DerivedLog が返されます。

使い方
--------

1. ログの出力先を初期化する

::

 sender = Sender({ 'type': 'syslogp',
                   'app': 'gokudo_gree' })

2. アクションログを作る

::

 actlog = ActionLog(sender, userid, device)

3. アクションログを出力する

::

 record = actlog.do_gacha(GachaType.FREE, 10)

4. 必要であれば子のアクションログを使って出力する

::

 actlog2 = record.get_actionlog()
 actlog2.do_quest(...)

5. 必要であれば派生ログを出力する

::

 actd = record.get_derivedlog()
 actd.dec_gachaticket('GACHA', ticket_id)

middlewareの利用
--------

Django 用の middleware を利用することで、便利にアクションログを出力できるようになります。

基本的に、アクションを with でツリー状にし、その中で派生ログを出力します。

以下のように利用します。 ::

 from kome.middleware.actionlog import log
 
 def gacha_view(self, request):
     # do_gachaアクション。必ず with で指定する。
     # 引数はdo_gachaに対する引数をキーワード引数で指定する。この時点では引数が足りなくても構わない。
     with log().do_gacha(gacha_type=GachaType.FREE):
         log().set(count=1, gacha_id='event10') # do_gacha アクションに対する引数を追加
         log().derivedlog.dec_gachaticket('GACHA', ticket_id) # 派生ログを出力
 
 def move_map_view(self, request):
     # アクションログのセクションで出した例は以下のように記述することで実現できる
     with log().do_quest(...):
         log().inc_card(...)
         with log().fusion_card(...):
             log().dec_card(...)

具体的な設定の手順は以下の通りです。 ::

1. middleware を設定する

::

 MIDDLEWARE_CLASSES = (
   ...
   'kome.middleware.actionlog.ActionLogMiddleware'
 }

2. settings.KOME_INFO にログの出力先を設定する

::

 KOME_INFO = { 'type': 'syslogp',
               'app': 'gokudo_gree' }

3. ログを出力する

::

 from kome.middleware.actionlog import log
 
 def view(self, request):
     with log().do_quest(...):
         pass

カスタムログの出力
-------

kome の利用者は通常、ライブラリ側で用意したデフォルトのログのみを利用します。
しかし、例えば特定のイベントのみでしか発生しないログや、アプリ固有のログを出力したい場合もあります。

こういった場合には、カスタムログを利用すると、任意のログを出力することができるようになります。 ::

 # イベント番号8固有のログ。ジェムを使ってキャラバンからカードを取得。
 record = actlog.log("e8_caravan_execute", # 第１引数はアクション名
                     # 以降は任意のキーワード引数
                     caravan_id="12",
                     color="red",
                     before_jewel=5,
                     after_jewel=2,
                     success=True)
 record.get_derivedlog().inc_card(...) # 増えたカードを派生ログとして出力
