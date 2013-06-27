# -*- coding: utf-8 -*-
"""
gsocial_model

"""

import datetime
from gsocial.log import Log
import warnings

from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.db import IntegrityError

from gsocial.set_container import Container, containername, containerdata
from gsocial.utils.people import People
from gsocial.utils.message import Message
from gsocial.setting import GREE, MOBAGE, GREE_NET
from gsocial.exceptions import ResponseError
from gamelog.models import DailyAccessLog

from horizontalpartitioning.models import HorizontalPartitioningModel



# 更新間隔 - 6時間
FRIEND_UPDATE_TERM = 21600

# 新規登録と判定するupdated_at
IS_NEW_DATE = datetime.datetime(1978 , 7, 12, 0, 0, 0)

#使わないのでコメントアウト
#AB_ELEMENT_KEY_ITEM = "ITEM"
#AB_ELEMENT_KEY_GACHA = "GACHA"
#AB_ELEMENT_KEY_BONUS = "BONUS"
#
#AB_ELEMENT_TYPE = {
#    AB_ELEMENT_KEY_ITEM:0,
#    AB_ELEMENT_KEY_GACHA:1,
#    AB_ELEMENT_KEY_BONUS:2,
#}

OPENSOCIAL_USER_FIELD_NAMES = set()

def has_opensocial_user_field(name):
    """
    has_opensocial_user_field
    """
    return name in OPENSOCIAL_USER_FIELD_NAMES

def deprecation(message):
    """
    Deprecation Warning
    """
    warnings.warn(message, DeprecationWarning, stacklevel=2)

class OpenSocialUser(HorizontalPartitioningModel):
    """
    opensocial_user_model
    """

    ResponseError = ResponseError

    def opensocial_user_delegate(classname, base_types, dict):
        """
        opensocial_user_delegate
        """
        cls = type(classname, base_types, dict)
        for field in cls._meta.fields:
            OPENSOCIAL_USER_FIELD_NAMES.add(field.name)
        return cls

    __metaclass__ = opensocial_user_delegate
    HORIZONTAL_PARTITIONING_KEY_FIELD = 'userid'

    userid = models.CharField(u'ユーザーID', max_length=255, primary_key=True)
    nickname = models.CharField(u'ニックネーム', max_length=255, null=False, blank=True)
    userType = models.CharField(u'ユーザータイプ', max_length=16, null=True, blank=True)
    birthday = models.DateField(u'誕生日', null=True, blank=True)
    # GREE: male, female, 空文字列のいずれかであり、空の場合は未設定か非公開
    gender = models.CharField(u'性別', max_length=16, null=True, blank=True)
    # 年齢
    age = models.IntegerField(u'年齢', default=0)
    # GREE: A, B, O, AB, 空文字列
    bloodType = models.CharField(u'血液型', max_length=16, null=True, blank=True)
    # GREE ではキャッシュ禁止なのでユーザサムネイルサービスを使う
    thumbnailUrl = models.CharField(u'サムネールURL', max_length=255, null=False, blank=True)
    # 以下 元々はOptionProfile だったもの
    profileUrl = models.CharField(u'プロフィールURL', max_length=255, null=False, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    friend_userids = models.TextField(u'友達のuseridをカンマ区切りで保存', blank=True) #DEPRECATED! People API を使う

    # デバッグ環境でのみ使う 水平分割では使えない
    #friends = models.ManyToManyField("self", null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        save
        """
        super(OpenSocialUser, self).save(*args, **kwargs)
        #self.set_cache()

    def delete(self, *args, **kwargs):
        """
        delete
        """
        cache_key = OpenSocialUser.get_cache_key(self.userid)
        cache.delete(cache_key) # 管理画面などで消す場合も消しておかないと大変
        super(OpenSocialUser, self).delete(*args, **kwargs)

    @staticmethod
    def get_cache_key(userid):
        """
        osuserを取得するためのキーを返す
        """
        return "/opensocialuser/" + str(userid)

    def set_cache(self):
        """
        osuserをキャッシュにセットする
        """
        path = OpenSocialUser.get_cache_key(self.userid)
        # People API の結果は24時間までキャッシュできる
        cache.set(path, self, timeout=24 * 60 * 60)

    class Meta:
        verbose_name = u'ユーザー'

    def __unicode__(self):
        return u"%s : %s" % (self.userid, self.nickname)

    # peopleAPI
    def is_male(self):
        """
        男性か？（Falseを返したからといって女性とは決定しないため注意
        """
        return self.gender == u'male'

    # peopleAPI
    def is_female(self):
        """
        女性か？（Falseを返したからといって男性とは決定しないため注意
        """
        return self.gender == u'female'

    # peopleAPI
    @property
    def profile_url(self):
        """
        プロフィールページのURL
        Arguments:
        - `self`:
        """
        if self.profileUrl:
            return self.profileUrl
        return containerdata["profile_url"] % {"userid":self.userid}

    # peopleAPI
    @property
    def profile_url_sp(self):
        """
        プロフィールページのURL
        Arguments:
        - `self`:
        """
        if self.profileUrl:
            return self.profileUrl
        return containerdata["profile_url_sp"] % {"userid":self.userid}

    # peopleAPI
    @property
    def thumbnail_url(self):
        """
        thumbnail_url
        """
        if containername == GREE:
            return 'thumbnail:show?user_id=%s&size=normal' % self.userid
        else:
            return self.thumbnailUrl

    # peopleAPI
    @property
    def thumbnail_url_s(self):
        """
        thumbnailUrlSmall を得る
        """
        if containername == GREE:
            return 'thumbnail:show?user_id=%s&size=small' % self.userid
        raise

    # peopleAPI
    @property
    def thumbnail_url_m(self):
        """
        thumbnailUrlMedium を得る
        """
        return self.thumbnail_url

    # peopleAPI
    @property
    def thumbnail_url_upper_m(self):
        """
        upperとentireはmbgaにしかない概念
        thumbnailUrl を得る
        """
        if containername == GREE:
            return self.thumbnail_url
        if containername == MOBAGE:
            return self.thumbnailUrlUpperMedium
        raise

    # peopleAPI
    @property
    def thumbnail_url_l(self):
        """
        thumbnailUrlLarge
        """
        if containername == GREE:
            return 'thumbnail:show?user_id=%s&size=large' % self.userid
        else:
            raise

    # peopleAPI
    @property
    def thumbnail_url_upper_l(self):
        """
        upperとentireはmbgaにしかない概念
        thumbnailUrlLarge を得る
        """
        if containername == GREE:
            return 'thumbnail:show?user_id=%s&size=large' % self.userid
        if containername == 'mbga':
            return self.thumbnailUrlUpperLarge
        raise

    # peopleAPI
    @property
    def thumbnail_url_h(self):
        """
        thumbnailUrlHuge を得る
        """
        if containername == GREE:
            return 'thumbnail:show?user_id=%s&size=huge' % self.userid
        raise

    def need_update(self):
        # 最終ログインから6時間経っていたらTrueを返す
        check_1 = not self.friend_userids or not self.nickname
        check_time = datetime.datetime.now() - datetime.timedelta(0, FRIEND_UPDATE_TERM)
        check_2 = self.updated_at < check_time
        return check_1 or check_2

    # peopleAPI
    def get_friend_userids(self):
        """
        友達のユーザーIDリストを返す
        """
        if self.friend_userids:
            if self.friend_userids == u'-':
                return []
            else:
                return self.friend_userids.split(',')
        else:
            return []

    # peopleAPI
    def get_friends(self, request):
        """
        DEPRECATED! People の API (get_friendsなど)を使ってください
        get_friends
        """
        deprecation('OpenSocialUser.get_friends. Use People API')
        friend_userids = self.get_friend_userids()
        friends = []
        for friend_opensocial_userid in friend_userids:
            user = self.get_friend_by_userid(request, friend_opensocial_userid)
            if user:
                friends.append(user)
        return friends

    # peopleAPI
    def get_friends_exclude(self, request, exclude_users):
        """
        DEPRECATED! People の API (get_friendsなど)を使ってください
        get_friends_exclude
        """
        deprecation('OpenSocialUser.get_friends_exclude. Use People API')
        friend_userids = self.get_friend_userids()
        friends = []

        for exclude_user in exclude_users:
            if exclude_user.userid in friend_userids:
                friend_userids.remove(exclude_user.userid)

        for friend_opensocial_userid in friend_userids:
            osuser = self.get_osuser_friend(friend_opensocial_userid, request)
            if osuser:
                friends.append(osuser)
        return friends

    # peopleAPI
    def update_profile(self, request):
        """
        プロフィールを更新する（成功の場合はTrue、失敗の場合はFalseを返す）
        Arguments:
        - `self`:
        - `request`:
        """
        #self.calc_group() #ABテストの振り分けを決定する
        if settings.OPENSOCIAL_DEBUG or settings.IS_STRESS_TEST:
            # 開発環境
            self.nickname = self.userid
            #friend_userids = [f.userid for f in self.friends.all()]
            # #水平分割の際、friendsは使わない
            #self.friend_userids = u",".join(friend_userids)
            self.updated_at = datetime.datetime.now()
        else:

            request_params = 'id,nickname,thumbnailUrl,profileUrl,gender,age,birthday,bloodType,userType,userGrade'
            profile = People(request).get_myself(self.userid, request_params, caching=False)
            # プロフィールを更新
            if profile:
                Log.debug(profile)
                if 'nickname' in profile and profile['nickname']:
                    self.nickname = profile['nickname']
                if 'thumbnailUrl' in profile and profile['thumbnailUrl']:
                    self.thumbnailUrl = profile['thumbnailUrl']
                if 'profilelUrl' in profile and profile['profileUrl']:
                    self.profileUrl = profile['profileUrl']
                if 'gender' in profile and profile['gender']:
                    self.gender = profile['gender']
                if 'age' in profile and profile['age']:
                    if profile['age'] == '':
                        age = 0
                    else:
                        age = int(profile['age'])
                    self.age = age
                if 'bloodType' in profile and profile['bloodType']:
                    self.bloodType = profile['bloodType']
                if 'userType' in profile and profile['userType']:
                    self.userType = profile['userType']
                result = True
            else:
                result = False

            # プラットフォームの友だち情報更新処理はここでは行わない!
            # 時間がかかるだけなので。URLError: <urlopen error timed out>
            # が出ることもある。
            # OpenSocialUser が持っているフレンド情報は使わないこと。
            # プラットフォームの友だちかどうかは、別処理で判断する。
            # 例えば、友だち一覧にゲーム内フレンド申請をする場合は、
            # People(request).get_friends(self.id, fields='id')['entry']
            # を直接呼ぶこと。
            # 例: gamecore1の module.player.models.friend.GreeFriendMixin の
            # gree_friend_ids を参照。
            # 友達情報を更新
#            report_exception = None #動作レポート用の例外。消しても良い
#            if request:
#                friend_userids = []
#                f_params = 'id,nickname,thumbnailUrl'
#                fdata = People(request).get_friends(self.userid, fields=f_params)
#                Log.debug("----------------------------------------------")
#                Log.debug(fdata)
#                Log.debug(fdata['entry'])
#                Log.debug("----------------------------------------------")
#                if fdata and 'entry' in fdata:
#                    for entry in fdata["entry"]:
#                        if settings.OPENSOCIAL_CONTAINER.endswith(GREE) or settings.OPENSOCIAL_CONTAINER.endswith(GREE_NET):
#                            if not entry:
#                                #entryが[]の場合があるので、回避
#                                #ただし、その場合はcontainerの通信内容を報告する
#                                report_exception = self.ResponseError("update_profile", "entry is not True.", container.latest_response)
#                                continue
#                            #idが無い場合は keyerror を raise で良いかな。とりあえずは。
#                            try:
#                                userid = entry["id"]
#                            except TypeError:
#                                # TypeError: list indices must be integers が出ることがある
#                                raise self.ResponseError("update_profile", "Get userid from entry.", fdata)
#                        else:
#                            _, userid = entry["id"].split(":")
#
#                        friend_userids.append(userid)
#
#                if friend_userids:
#                    self.friend_userids = u",".join(friend_userids)
#                elif not self.friend_userids:
#                    # 空の場合は、-を入れておく
#                    self.friend_userids = u"-"
            #保存
            self.updated_at = datetime.datetime.now()
            self.update_thumbnail(request)

#            if report_exception:
#                #通信エラーが合った場合は報告する
#                raise report_exception
            return result

    # peopleAPI
    def update_friend_profile(self, request, friend):
        """
        DEPRECATED! People の API (get_friendsなど)を使ってください
        友達のプロフィールを更新する
        Arguments:
        - `self`:
        - `request`:
        - `osuser`:
        """
        deprecation('OpenSocialUser.update_friend_profile. Use People API')
        if not settings.OPENSOCIAL_DEBUG:
            container = Container(request)
            profile = container.get_friend(self.userid, friend.userid, fields='id,nickname,thumbnailUrl')
            # プロフィールを更新
            if profile and 'nickname' in profile and profile['nickname']:
                friend.nickname = profile['nickname']
            if profile and 'thumbnailUrl' in profile and profile['thumbnailUrl']:
                friend.thumbnailUrl = profile['thumbnailUrl']

            friend.updated_at = datetime.datetime.now()
            friend.update_thumbnail(request)
            friend.save()

    # peopleAPI
    def update_thumbnail(self, request):
        """
        サムネイルを更新する
        """
        if not settings.OPENSOCIAL_DEBUG:
            container = Container(request)
            # モバゲーのサムネイル更新
            if containername == 'mbga':
                params = 'size=medium;dimension=defined;emotion=normal;transparent=true;view=upper'
                upper_m = container.get_mbga_avatar_self(self.userid, params=params)
                params = 'size=large;dimension=defined;emotion=normal;transparent=true;view=upper'
                upper_l = container.get_mbga_avatar_self(self.userid, params=params)
                if upper_m:
                    self.thumbnailUrlUpperMedium = upper_m.get('url', '')
                if upper_l:
                    self.thumbnailUrlUpperLarge = upper_l.get('url', '')

    # peopleAPI
    def get_friend_by_userid(self, request, friend_opensocial_userid):
        """
        DEPRECATED! People の API (get_friendsなど)を使ってください
        osuseridから友達を取得する
        友人から作られるプロフィールは、
        ニックネームとサムネイルURLしかないため、DBに保存せずキャッシュにのみ保存する
        """
        deprecation('OpenSocialUser.get_friend_by_userid. Use People API')
        # キャッシュにない場合は、People APIからとってこないといけない
        friend_osuser = cache.get(OpenSocialUser.get_cache_key(friend_opensocial_userid))
        if friend_osuser is None:
            # キャッシュにないならインスタンス化するがDBにはいれないようにする
            friend_osuser = OpenSocialUser(userid=friend_opensocial_userid)
            # 友だちの権限でのみPeople APIを使って更新
            self.update_friend_profile(request, friend_osuser)
            # 友だち用に作られたインスタンスである事を判別するように
            try:
                OpenSocialUser.objects.get(userid=friend_opensocial_userid)
                friend_osuser.friend_cache = False
            except OpenSocialUser.DoesNotExist:
                # DB にはない事を示すフラグ
                friend_osuser.friend_cache = True
            # DB にいらなくね？
            friend_osuser.set_cache()
        return friend_osuser


# peopleAPI
def get_osuser(opensocial_user_id, request=None):
    """
    osuser を opensocial_user_id から取得。該当者がいない場合は None
    24時間で自動的にキャッシュがきれる筈なので、その間隔で更新する
    """
    #リクエストキャッシュ 1リクエスト内で同じget_osuser を複数回実行しない
    if request is not None:
        Log.debug('[OPENSOCIAL] get_osuser: call. useid=%s' % opensocial_user_id)
        request_cache = getattr(request, '_get_osuser_cache', {})
        if opensocial_user_id in request_cache:
            Log.debug('[OPENSOCIAL] get_osuser: request_cache hit. useid=%s' % opensocial_user_id)
            return request_cache[opensocial_user_id]
    osuser = cache.get(OpenSocialUser.get_cache_key(opensocial_user_id))
    if osuser is None or (hasattr(osuser, 'friend_cache') and osuser.friend_cache):
        # キャッシュに存在しないか存在してもfriendの場合
        # キャッシュに存在しない場合、タイムアウトしたならPeople APIを再度呼び出してキャッシュする
        # モデルに存在しない場合は新規作成
        update_profile_result = False
        try:
            # 存在確認だけ
            osuser = OpenSocialUser.objects.partition(opensocial_user_id).get(userid=opensocial_user_id)
            update_profile_result = osuser.update_profile(request) # GET でPeople APIを呼び出して更新する
        except OpenSocialUser.DoesNotExist:
            # 初作成の筈（set_cacheは内部で行われない）
            try:
                osuser = OpenSocialUser.objects.partition(opensocial_user_id).create(userid=opensocial_user_id)
                update_profile_result = osuser.update_profile(request) # GET でPeople APIを呼び出して更新する
            except IntegrityError:
                # duplicateすることがある
                return osuser
        if update_profile_result:
            osuser.set_cache()
    if request is not None:
        request_cache[opensocial_user_id] = osuser
        request._get_osuser_cache = request_cache
    return osuser

    # 以前の実装
    path = OpenSocialUser.get_cache_key(opensocial_user_id)
    osuser = cache.get(path, None)
    if osuser is None:  # キャッシュに存在しない
        try:
            osuser = OpenSocialUser.objects.partition(opensocial_user_id).get(userid=opensocial_user_id)
            osuser.set_cache()
        except OpenSocialUser.DoesNotExist:
            osuser = None
    return osuser

class PaymentInfo(models.Model):
    """
    購入情報
    """
    osuser_id = models.CharField(u'購入したプレイヤーのosuserid', max_length=50, null=False)
    item_id = models.IntegerField(u'購入したアイテムのid', max_length=50, null=False)
    point = models.IntegerField(u'購入したアイテムのpoint', null=False)
    quantity = models.IntegerField('購入したアイテムの個数', default=1)
    send_data = models.TextField(u'生送信データ', null=False)
    point_code = models.CharField(u'ポイント決済コード', max_length=50, unique=True)
    point_date = models.CharField(u'ポイント決済情報作成日時(UTC)', max_length=50, blank=True)
    point_url = models.URLField(u'モバイルポイントインタフェースURL', max_length=255, blank=True)
    recv_data = models.TextField(u'受信生データ', null=True)
    status = models.CharField(u'購入ステータス', max_length=50, null=True, blank=True)
    device = models.IntegerField(u'購入プレイヤーのデバイスタイプ', default=1)
    created_at = models.DateTimeField(u'作成日時', auto_now_add=True, editable=False)

    class Meta:
        verbose_name = u'購入情報'
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return unicode(self.osuser_id) + u'の購入情報'

    @classmethod
    def get_by_point_code(cls, point_code):
        """
        ポイントコードからインタンスを取得する
        """
        return cls.objects.get(point_code=point_code)

    def is_succeeded(self):
        """
        購入成功していたらTrue
        """
        return int(self.status) == int(Container().payment_success_status)

    def is_canceled(self):
        """
        購入キャンセルされていたらTrue
        """
        return int(self.status) == int(Container().payment_cancel_status)

    def save_as_succeeded(self):
        """ 購入成功として保存する
        """
        self.status = Container().payment_success_status
        self.save()

    def save_as_canceled(self):
        """ 購入キャンセルとして保存する
        """
        self.status = Container().payment_cancel_status
        self.save()


# messageAPI
# どのコンテナでも実体化するモデル（コンテナ要求に満たない場合、モデルを変更してください）
class MessageInfoBase(models.Model):
    """
    Message API に送信する情報（ただし、運営のみ？）
    現状はGREEの仕様に準じているため、mixiなどのコンテナで利用する際にはmigrateすることを想定すること
    ・titleおよびbodyフィールドには、ユーザーによる自由入力文を設定してはいけない。
    ・titleフィールドは全角13文字（半角26文字）以内。制限を超えた場合制限文字数に省略。
    ・bodyフィールドは全角50文字（半角100文字）以内。制限を超えた場合制限文字数に省略。
    """

    title = models.CharField(u'タイトル', max_length=26, null=False, help_text=u'全角13文字、半角26文字以内')
    body = models.TextField(u'本文', max_length=100, null=False, help_text=u'全角50文字、半角100文字以内')
    url = models.CharField(u'リンク先URL', max_length=50, null=True, blank=True)
    sent = models.BooleanField(u'送信済み', default=False, null=False) # 送信済みフラグ
    created_at = models.DateTimeField(u'作成日時', auto_now_add=True, editable=False)

    class Meta:
        proxy = False
        verbose_name = u'Message API'
        verbose_name_plural = verbose_name

    def send_message(self, request):
        Log.debug('send_message Base.')
        # 自身の持つデータを全員に送信する
        #opensocial_users = OpenSocialUser.objects.all()
        player_list = DailyAccessLog.objects.all().values('osuser_id').distinct()

        send_player_list = []
        for player_dict in player_list:
            send_player_list.append(player_dict['osuser_id'])

        #message = Message(request)

        #container = osrequest.Container(request)
        #for opensocial_user in opensocial_users:
        for user in send_player_list:
            # 全員に自身のメッセージを送信
            #message.send(None, opensocial_user.userid, self.title, self.body, self.url)
            Message().send(None, user, self.title, self.body, self.url)
            #container.send_message(None, opensocial_user.userid, self.title, self.body, url)

# 端末識別認証
class AuthDevice(HorizontalPartitioningModel):
    """
    端末識別情報保存用モデル
    """
    osuser_id = models.CharField(max_length=255, primary_key=True)
    auth_id = models.CharField(u'識別値', max_length=255, blank=True, null=True, default=None, db_index=True)
    is_authorized = models.BooleanField(u'認証済みか', default=False, null=False)

    created_at = models.DateTimeField(u'作成日時', auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(u'更新日時', auto_now_add=True, auto_now=True, editable=False)
    #userGrade(GREE)
    user_grade  =  models.CharField(u'userGrade', max_length = 10, blank = True)

    HORIZONTAL_PARTITIONING_KEY_FIELD = 'osuser_id'

class MonthlyPaymentInfo(models.Model):
    """
    購入情報
    """
    osuser_id = models.CharField(u'購入したプレイヤーのosuserid', max_length=50, null=False)
    created_at = models.DateTimeField(u'作成日時', auto_now_add=True, editable=False)
    transaction_id = models.CharField(u'トランザクションID', max_length=255, unique=True)
    service_id = models.CharField(u'サービスID', max_length=255, unique=True)
    status = models.IntegerField(u'status', max_length=10, null=False)
    resubscribe = models.IntegerField(u'status', max_length=10, null=False)
    ordered_time = models.DateTimeField(u'注文日時', null=False)
    excute_time = models.DateTimeField(u'登録確定日時', null=False)


