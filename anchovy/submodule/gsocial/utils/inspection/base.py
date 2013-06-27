# -*- coding: utf-8 -*-
"""
InspectionAPI
"""

from gsocial.set_container import Container


class InspectionBase(object):
    """
    Inspection基底クラス
    """
    RETRY_COUNT = 3

    # API が返すStatus定数
    STATUS_INSPECTING = 0 # 監査中
    STATUS_OK         = 1 # 監査結果OK
    STATUS_DELETE     = 2 # 削除
    STATUS_NG         = 3 # 監査結果NG

    def __init__(self, request = None):
        # OpenSocialのContainerを作成する
        self.container = Container(request)

    def _get_cache_key(self):
        """
        キャッシュキー生成
        """
        pass

    def _api_path(self):
        """
        apiのpath生成
        """
        pass

    def _api_request(self):
        """
        apiへのrequest処理
        """
        pass
