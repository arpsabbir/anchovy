# -*- coding: utf-8 -*-
"""
auth_device base class
"""
from django.core.cache import cache
from django.conf import settings

from gsocial.set_container import Container
from gsocial.models import AuthDevice, get_osuser
from gsocial.utils.base import GsocialCache
from error import AuthDeviceError

from gsocial.log import Log


class AuthRecord(object):
    """
    認証レコード
    AuthDeviceManagerが主に使う
    """
    CACHE_TIMEOUT = 3600  # キャッシュタイムアウト値

    def __init__(self, request, user_id=None):
        if user_id:
            self.osuser = get_osuser(user_id)
            if not self.osuser:
                raise AuthDeviceError('Can not find user. UserID=%s' % str(user_id))
        else:
            self.osuser = request.osuser
        self.user_id = self.osuser.userid

    @property
    def cache_key(self):
        """
        キャッシュのキー名を返す
        """
        return '/opensocial/authdevice/model/%s' % self.user_id

    def get_record(self):
        """
        認証レコード取得
        AuthDeviceモデルインスタンスを返す
        """
        auth = GsocialCache.get_cache(self.cache_key)
        if auth is None:
            try:
                auth = AuthDevice.objects.partition(self.user_id).get(osuser_id=self.user_id)
                if AuthDeviceManager.check_user_grade(auth.user_grade):
                    timeout = self.CACHE_TIMEOUT
                    GsocialCache.set_cache(self.cache_key, auth, timeout)
                    # グレード 3以下はキャッシュしない
                    # 従来は 3600秒キャッシュしていた
            except AuthDevice.DoesNotExist:
                auth = None
        return auth

    def create_record(self, auth_id, is_authorized = False, user_grade=None):
        """
        認証レコード作成
        作成したAuthDeviceモデルインスタンスを返す
        """
        Log.debug('Check is_authorized.', is_authorized)
        auth = AuthDevice.objects.partition(self.user_id).create(
                osuser_id=self.user_id, auth_id=auth_id,
                user_grade=user_grade, is_authorized=is_authorized)
        GsocialCache.set_cache(self.cache_key, None, 1) # キャッシュ削除
        return auth

    UPDATABLE_COLUMNS = set(['auth_id', 'is_authorized','user_grade'])
    def update_record(self, record, **argv):
        """
        認証レコード更新
        """
        for name, value in argv.iteritems():
            if name in self.UPDATABLE_COLUMNS and hasattr(record, name):
                setattr(record, name, value)
        record.save()
        GsocialCache.set_cache(self.cache_key, None, 1) # キャッシュ削除


class AuthAPI(object):
    """
    認証API
    AuthDeviceManagerが主に使う
    """
    CACHE_TIMEOUT = 3600  # キャッシュタイムアウト値

    def __init__(self, request, user_id=None):
        self.request = request
        self.container = Container(request)
        self.user_id = user_id if user_id else request.osuser.userid

    @property
    def cache_key(self):
        """
        APIキャッシュのキー名を返す
        """
        return '/opensocial/authdevice/api/%s' % self.user_id

    def get_auth_id(self):
        """
        APIによる 識別ID取得
        キャッシュ制御も行う
        """
        auth_id = GsocialCache.get_cache(self.cache_key)
        if auth_id is None:
            auth_id = self._get_auth_id(self.user_id)
            if auth_id:
                GsocialCache.set_cache(self.cache_key, auth_id, self.CACHE_TIMEOUT)

        return auth_id if auth_id else None

    def _get_auth_id(self, userid):
        """
        APIによる 識別ID取得（プラットフォーム依存部）
        """
        raise NotImplementedError

    @property
    def user_grade_cache_key(self):
        """
        APIキャッシュのキー名を返す
        """
        return '/opensocial/authdevice/api/user_grade/%s' % self.user_id

    def get_auth(self):
        """
        APIによる 識別ID/UserGrade取得
        キャッシュ制御も行う
        """
        #cache.set(self.user_grade_cache_key, None, 1)
        user_grade = GsocialCache.get_cache(self.user_grade_cache_key)
        auth_id = GsocialCache.get_cache(self.cache_key)

        if user_grade is None:
            auth_id, user_grade = self._get_auth(self.user_id)
            if user_grade:
                GsocialCache.set_cache(self.user_grade_cache_key, user_grade, self.CACHE_TIMEOUT)
            else:
                user_grade = None

            if auth_id:
                GsocialCache.set_cache(self.cache_key, auth_id, self.CACHE_TIMEOUT)
        return [auth_id, user_grade]

    def _get_auth(self, userid):
        """
        APIによる 識別ID取得/UserGrade（プラットフォーム依存部）
        """
        raise NotImplementedError


class AuthDeviceManager(object):
    """
    端末認証マネージャ
    """
    def __init__(self, request, apiclass, user_id=None):
        """
        コンストラクタ
        """
        self.request = request
        self.user_id = user_id if user_id else request.osuser.userid # ユーザID
        self.recmanager = AuthRecord(request, user_id=user_id)
        self.apimanager = apiclass(request, user_id=user_id)
        self._auth_id = None # 識別ID
        self._user_grade = None # UserGrade
        self._is_auth_device = False # 端末認証がされているか

        ### 認証チェック処理

        # ローカルの場合、強制的に端末認証済みとする
        if getattr(settings, 'OPENSOCIAL_DEBUG', False):
            self._is_auth_device = True
            return

        # 認証レコード取得
        self._authrec = self.recmanager.get_record()
        if self._authrec:
            # 認証レコードが存在した場合
            if self._authrec.is_authorized:
                # 端末認証が既に行われている場合True
                self._auth_id = self._authrec.auth_id
                self._is_auth_device = True
        else:
            # APIから端末認証IDを取得
            user_grade = None
            auth_id = None
            auth_id, user_grade = self.apimanager.get_auth()
            if AuthDeviceManager.check_user_grade(user_grade):
                # 認証レコード作成（認証済み）
                self._authrec = self.recmanager.create_record(auth_id, True, user_grade)
                self._auth_id = auth_id
                self._user_grade = user_grade
                self._is_auth_device = True
            else:
                # 認証レコード作成（未認証）
                self._authrec = self.recmanager.create_record(None, False, user_grade)

    @property
    def auth_id(self):
        """
        端末認証IDを返す。未認証の場合はNone
        """
        return self._auth_id

    @property
    def user_grade(self):
        """
        UserGradeを返す。未認証の場合はNone
        """
        return self._user_grade

    @property
    def is_auth_device(self):
        """
        端末認証済みか
        Falseの場合、self.check_auth_device()を呼ぶ必要がある
        """
        return self._is_auth_device

    def check_auth_device(self):
        """
        端末認証の実際のチェックを行う
        戻り値:
            True: 端末認証処理完了
            False: 端末認証処理未実施
        """
        if self.is_auth_device:
            # （普通は通らないが）端末認証が既に行われている場合、未実施扱いとする
            return False

        if self._authrec:
            # APIから端末認証IDを取得
            auth_id, user_grade = self.apimanager.get_auth()
            if user_grade:
                is_authorized_flag = False
                if AuthDeviceManager.check_user_grade(user_grade):
                    is_authorized_flag = True
                # 端末認証IDを取得できた場合、認証レコードを更新
                self.recmanager.update_record(self._authrec, auth_id=auth_id,
                                            user_grade=user_grade,
                                             is_authorized = is_authorized_flag)
                self._auth_id = auth_id
                self._is_auth_device = is_authorized_flag
                return is_authorized_flag

        # レコードが存在しない場合、APIから取得できない場合は認証処理はできない
        self._auth_id = None
        return False

    @classmethod
    def check_user_grade(cls, user_grade):
        """
        user_grade_check

        返り値:
        user_gradeが'3'の場合 => True
        user_gradeが'3'以外の場合 => False
        """
        if user_grade:
            if user_grade == '3':
                return True
        return False

    @classmethod
    def _cache_clear(cls, user_id):
        """
        cache_clear
        """
        auth_model = '/opensocial/authdevice/model/%s' % user_id
        user_grade = '/opensocial/authdevice/api/user_grade/%s' % user_id
        auth_id = '/opensocial/authdevice/api/%s' % user_id

        GsocialCache.delete_cache(auth_model)
        GsocialCache.delete_cache(user_grade)
        GsocialCache.delete_cache(auth_id)
