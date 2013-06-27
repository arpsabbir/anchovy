GToolKit
==========

別レポジトリに分けるほどでもない便利ライブラリ的な物

cache
-----------

キャッシュ機能を追加するためのライブラリ。

memoized_property
    インスタンス内でプロパティの結果をキャッシュする
method_cache
    クラスメソッドをcache化する
CachedMasterModel
    models.Modelに基本的なキャッシュ機能(単体(get)と全て(get_all))を実装したもの

db
-----------

django.Model関連のライブラリ

FakedMasterModel
    CachedMasterModelに似たインターフェイス(get, get_all)を持つ、素のPythonクラス。
    DBを使うまでもないマスターデータなどで使用。fixturesにdictで設定した値がデータとして扱われる
EnableFlagMixin
    is_enableフィールドが追加され、このフィールドがTrueでないとgetなどに現れない。
    delete()はis_enableフィールドがFalseになるだけになる。
UniqueIDFieldMixin
    unique_idフィールドを追加する。
    中身のuuidはcreate時に自動で付与され、物理サーバーを跨いで一意である事が補償される。
NameFieldMixin
    nameとdescriptionフィールドを追加する
DateTimeFieldMixin
    created_atとupdated_atフィールドを追加する。
    それぞれ自動で入力/更新される。
TermMixin
    start_atとend_atフィールドが追加され期間を表現できる。
    期間内であればis_in_termプロパティがTrueになる。
MonthlyCycleMixin
    毎月のmonth_start_at日~month_end_at日にis_activeがTrueになる
WeeklyCycleMixin
    毎週week曜日にis_activeがTrueになる
DailyCycleMixin
    毎日day_start_at時〜day_end_at時にis_activeがTrueになる

math
-----------

計算ライブラリ。ベジェ曲線の計算やグラフの計算ロジックがある。
主に成長曲線の表現などに使われている。


redis
-----------

旧KVSライブラリにおけるGeneric.KVSのインターフェイスをgRedisとgKVSを用いて実装したもの


animation
-----------

swfとgumi製HTML5アニメーションを自動で判別し、レンダーする為の仕組み。

image
-----------

画像のパス等をインスタンスとして扱う為のクラス群。
ImageMixinを継承するとインスタンスに .image プロパティが生える。
それらを扱うテンプレートタグ(image, image_url)が含まれており、アクセスにFP/SPに応じた


once_lock
-----------

viewの返り値を規定時間の間キャッシュしてviewのロジックを通らずに前回の表示をそのまま表示するデコレータ


pager
-----------




======
test
======

::

    $ cd gtoolkit
    $ nosetests







