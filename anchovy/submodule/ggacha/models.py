# -*- coding: utf-8 -*-
"""
ggacha は Player モデルに依存しているため,
初めに抽象クラス PlayerModelMixin を継承した,
ゲーム毎の実装クラスを作成する必要がある.


アプリの基盤として gsc を用いる場合, 次の通り.

.. code-block:: python

    from ggacha.models import PlayerModelMixin as GPlayerModelMixin

    from module.player import get_player

    class PlayerModelMixin(GPlayerModelMixin):
        def get_player(self, player_id):
            return get_player(player_id)


request に player プロパティを持つゲームの場合, 次の通り.

.. code-block:: python

    from ggacha.models import OldStylePlayerModelMixin

    from module.player.decorators import require_player
    from module.player.api import get_player

    class PlayerModelMixin(OldStylePlayerModelMixin):
        def get_player_from_request(self, request):
            request = require_player(lambda *args, **kwargs: args[0])(request)
            return request.player

        def get_player(self, player_id):
            return get_player(player_id)


これを /path/to/gacha/impl/models.py 等に保存して使用する.
"""
from ggacha.utils import RaiseExceptionMixin

class PlayerModelMixin(RaiseExceptionMixin):
    """
    Player モデルを取得する抽象 Mix-in クラス

    View に player プロパティが存在している事が前提.
    """
    def get_player(self, player_id):
        """
        player_id から Player モデルを返す処理を記述する.

        :param int player_id: プレイヤーID.
        :return: Player オブジェクト
        :raises: NotImplementedError

        このメソッドを上書きしていない場合, NotImplementedError が発生する.
        """
        self.raise_not_impl('get_player')

    def init_player(self, request):
        """
        gsc の View では, self.player に player モデルが存在しているため,
        init_player で行う処理は存在しない.
        """
        pass


class OldStylePlayerModelMixin(PlayerModelMixin):
    """
    request に player プロパティが存在している
    古いスタイルのゲームに対応した PlayerModelMixin.

    View に player プロパティを追加する.
    """
    def get_player_from_request(self, request):
        """
        request の opensocial_userid から Player モデルを作成して
        返す処理を記述する.

        :param HttpRequest request: リクエストオブジェクト.
        :return: Player オブジェクト
        :raises: NotImplementedError

        このメソッドを上書きしていない場合, NotImplementedError が発生する.
        """
        self.raise_not_impl('get_player_from_request')

    def init_player(self, request):
        if hasattr(self, '_player'):
            return
        self._player = self.get_player_from_request(request)

    @property
    def player(self):
        self.raise_if_none('_player')
        return self._player
