
jsonmastermodel
===============

gtoolkit.db.jsonmastermodel の独立版

gtoolkit.db.jsonmastermodel との違い
------------------------------------

gtoolkit のものは、フィールドの定義は必要なかったが、
こちらはフィールド定義が必須となっている。

置き換える場合は、この name のように明示的なフィールド定義を行うこと。

name フィールドを定義する場合::

    class MockModel(JsonMasterModel):
        name = JsonMasterNameField()


モデル記述例
------------

実際の使用例は tests/models.py を見てほしいが、このように使う::

    from jsonmastermodel import JsonMasterModel, JsonMasterField

    class MockModel(JsonMasterModel):
        MASTER_DATA_JSON_PATH = '%s/jsonmastermodel-testfixture.json' % \
                                os.path.dirname(__file__)

        name = JsonMasterNameField()
        value = JsonMasterIntField()
        detail_text = JsonMasterTextField()


gamecore系であれば、MASTER_DATA_JSON_PATH は、プロジェクトの data ディレクトリからの
相対値でも動作する。
シーケンスであれば、os.path.sep で連結してファイルにアクセスする。

MASTER_DATA_JSON_PATH にシーケンスを指定する例::

    class QuestM(JsonMasterModel):

        MASTER_DATA_JSON_PATH = 'quest', 'questm.json'


モデル使用例
------------

.objects. が Djangoのモデルマネージャに似た動作をするので、このように使える::

    MockModel.objects.get(category=10, seq=3)
    MockModel.objects.filter(category=10)
    MockModel.objects.get_by_id(2)

CachedMasterModel のメソッドも一部使える::

    MockModel.get(2)
    MockModel.get_all()

インデックス検索の代用となる高速検索もある::

    MockModel.quick_filter(category=10)
