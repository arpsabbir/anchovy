===============
Gsocialとは
===============

GreeAPIなどのプラットフォームと中継を行なってくれるDjangoアプリケーション


Settingについて
---------------
setting.pyに設定する項目::

    #デバッグモード指定
    OPENSOCIAL_DEBUG = True

    #サンドボックスモード指定
    OPENSOCIAL_SANDBOX = True

    #使用するコンテナー設定
    OPENSOCIAL_CONTAINER = 'sb.gree'

    #ID指定
    APP_ID = '13145'

    #CONSUMER_KEY指定
    CONSUMER_KEY = "14ab41f03a54"

    #CONSUMER_SECRET指定
    CONSUMER_SECRET = "ac62b878eb9d4d9697bfeaef6de58bb1"


利用できるAPI一覧
-------------------------

・ Activity_.

・ AuthDevice_.

・ BlackList_.

・ Inspection_.

・ Message_.

・ Payment_.

・ People_.

・ Request_.


利用できるTemplatetags一覧
-------------------------

・ ひとことサービス_.

・ リクエストサービス_.


API利用方法
---------------------------

.. _Activity:
*Activity*

1. Activityを送る ::

    from gsocial.utils.activity import Activity
    Activity(request).send(userid, title, url=None)
    input
        request: Djangoのrequestオブジェクト
        userid: opensocial_owner_id
        title: アクティビティのタイトル設定
    output
        None

.. _AuthDevice:

*AuthDevice*

1. 端末認証済みかどうかの確認:

    from gsocial.utils.authdevice.api import get_auth_device_api
    get_auth_device_api(request).is_auth_device
    input
        request: Djangoのrequestオブジェクト
    output
        True: 認証済み
        False: 非認証


2. 端末認証の実施 ::

    from gsocial.utils.authdevice.api import get_auth_device_api
    get_auth_device_api(request).check_auth_device
    input
        request: Djangoのrequestオブジェクト
    output
        True: 端末認証処理完了
        False: 端末認証処理未実施


.. _BlackList:
*BlackList*

1. ユーザーAがユーザーBをブラックリストに登録しているか判定する ::

    from gsocial.utils.blacklist import BlackList
    BlackList(request).blacklist_check(userid, target_userid)
    input
        request: Djangoのrequestオブジェクト
        userid: ユーザーAのID
        target_userid: ユーザーBのID
        caching: キャッシュするか defalut:True
        cache_update: キャッシュをアップデートするか defalut: False
    output
        True: 登録されている
        False: 登録されている


.. _Inspection:
*Inspection*

1. text投稿 ::

    from gsocial.utils.inspection import Inspection
    Inspection(request).post(userid, message)
    input
        request: Djangoのrequestオブジェクト
        userid: 投稿したopensocialowner_id
        message: 投稿文言
    output
        inspectionAPIのtext_id

2. text更新機能 ::

    from gsocial.utils.inspection import Inspection
    Inspection(request).put(userid, text_id, message)
    input
        request: Djangoのrequestオブジェクト
        text_id: 更新対象のtext_id
        userid: opensocial_owner_id
        message: 投稿内容
    output
        None

3. text削除機能 ::

    from gsocial.utils.inspection import Inspection
    Inspection(request).delete(userid, text_id, message)
    input
        request: Djangoのrequestオブジェクト
        text_id: inspection_id
        userid: opensocialowner_id
    output
        None


4. text取得 ::

    from gsocial.utils.inspection import inspection
    Inspection(request).gets_dict(userid, text_ids)
    input
        request: Djangoのrequestオブジェクト
        text_ids: text_idのリスト
        userid: opensocial_owner_id
        caching: キャッシュするか defalut:True
        retry_count: API接続できなかった時のリトライ回数
    output
        {text_id:(data, json, entry)}

        ※ data, json, entry はhash

        json, entry, dataのサンプル
            {
                "entry": [
                  {
                    "textId": "0123456-1",
                    "appId": "1001",
                    "authorId": "0123456",
                    "ownerId": "0123456",
                    "data": "自由な入力文",
                    "status": "0",
                    "ctime": "2010-04-29T14:41:00",
                    "mtime": "2010-04-29T14:41:00"
                  }
                ]
            }



5. text複数取得 ::

    from gsocial.utils.inspection import inspection
    Inspection(request).gets_dict(userid, text_ids)

    input
        request: Djangoのrequestオブジェクト
        text_ids: text_idのリスト
        userid: opensocial_owner_id
        caching: キャッシュするか defalut:True
        retry_count: API接続できなかった時のリトライ回数
    output
        [text_id:(data, json), ...]
        ※ data, json, はhash

6. text複数取得 ::

    from gsocial.utils.inspection import inspection
    Inspection(request).gets(userid, text_ids)

    input
        request: Djangoのrequestオブジェクト
        text_ids: text_idのリスト
        userid: opensocial_owner_id
        caching: キャッシュするか defalut:True
        retry_count: API接続できなかった時のリトライ回数
    output
        [text_id:(data, json, entry), ...]
        ※ data, json, entry はhash

.. _Message:
*Message*

1. 1ユーザーへの送信 ::

    from gsocial.utils.message import Message
    Message().send(sender_osuser_id, osuser_id, title, body, relative_mobile_url)

    input
        sender_osuser_id: 送り側のID(いらない)
        osuser_id: 対象ユーザーid
        title: メッセージタイトル
        body: メッセージ文言
        relative_mobile_url: メッセージのリンクURL
    output
        oauth_requstの戻り値


2. 複数ユーザーへの送信(Max 20人)
   ::

    from gsocial.utils.message import Message
    Message().sends(sender_osuser_id, osuser_ids, title, body, relative_mobile_url)
    input
        sender_osuser_id: 送り側のID(いらない)
        osuser_ids: 送信対象ユーザーidのリスト
        title: メッセージタイトル
        body: メッセージ文言
        relative_mobile_url: メッセージのリンクURL
    output
        oauth_requstの戻り値

.. _Payment:
*Payment*

1. 決済開始処理

   決済情報をレコードに保存し、GREEなどの決済ページへのURLを返す
   ::

    from gsocial.utils.payment import Payment
        pay_cls = Payment(request)
        res = pay_cls.request_payment(
        osuser_id = request.osuser.userid
        item_id = 1
        item_name = "アイテム名"
        item_point = 100
        item_description = "アイテム説明文"
        item_image_url = "http://%s" % settings.SITE_DOMAIN
        callback_path = reverse("debug_opensocial_payment_callback")
        finish_path = reverse("debug_opensocial_payment_finish")
        item_message = "メッセージ(GREEのみ) default=''"
        item_quantity = 1
        is_test = False
        )

    input
        request: Django requestインスタンス
        osuser_id: OpensocialUserのID
        item_id: アイテムID アイテムを識別するためのID
        item_name: アイテム名
        item_point: アイテム価格
        item_description： アイテム説明文
        item_image_url: アイテム画像のURL
        callback_url: コールバックURL
        finish_url: 購入処理後のFinishURL
        item_message: メッセージ(GREEのみ) default=''
        item_quantity: アイテムの個数 default=1
        is_test: テストフラグ(mixiのみ有効) default=False
    output
        payment_url: API側の決済ページURL

2. 決済コールバック処理

   Greeなどの決済ページからのコールバック処理の受け口。

   PaymentStatusの更新をおこうなう
   ::

    from gsocial.utils.payment import Payment
    Payment(request).callback()
    input
        request: Django requestオブジェクト
    output
        True:  購入完了
        False: 購入キャンセル

3. 決済Ｆｉｎｉｓｈ処理

   コールバック後の決済finish処理
   ::

    from gsocial.utils.payment import Payment
    Payment(request).finish()
    input
        request: Django requestオブジェクト
    output
        True:  購入完了
        False: 購入キャンセル

4. Payment決済情報確認

   ::

    from gsocial.utils.payment import Payment
    Payment(request).is_success()
    input
        request: Django requestオブジェクト
    output
        True:  購入完了
        False: 購入キャンセル

.. _People:
*People*

1. ユーザーの本人情報を取得する
   ::

    from gsocial.utils.people import People
    People(request).get_myself()
    input
        userid: 取得対象のopensocial_owner_id
        fields: 取得したいフィールド情報(指定しない場合すべての情報を取得する) defalut: None
           ext id,nicknameだけを取る場合
              'id,nickname'
        caching: キャッシュするか defalut:True
        cache_update: キャッシュをアップデートするか defalut: False
    output
         {
         "id": "0123456",
         "nickname": "グリーアプリ"
         }

         のようなhash

2. ユーザーAがユーザーBとソーシャル友達か確認
   ::

    from gsocial.utils.people import People
    People(request).get_friend(userid, friend_userid):
    input
        userid: ユーザーAのopensocial_owner_id
        friend_userid: ユーザーBのopensocial_owner_id
        caching: キャッシュするか defalut:True
        cache_update: キャッシュをアップデートするか defalut: False
    output
        情報がなかった場合: None
        情報があった場合: 下記のようなHashが帰ってくる
            {
            "nickname": "ナミ",
            "profileUrl": "http://gree.jp/0123457",
            "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
            }

3. ソーシャル友達を取得する

   仕様に則りGsocialではキャッシュしない

   一度のリクエストで100件単位で取得し、最大10回行う

   ::

    from gsocial.utils.people import People
    People(request).get_friends(self, userid, has_app=True, fields=None)
    input
        userid: opensocial_owner_id
        has_app: アプリをやっているユーザーを対象にするかどうか defalut:True
        fields: 取得したいフィールド情報(指定しない場合すべての情報を取得する) defalut: None
           ext id,nicknameだけを取る場合
              'id,nickname'
    output
        取得できた場合:
            {
            "totalResults": 4,
            "itemsPerPage": 5,
            "entry": [
              {
                "nickname": "ナミ",
                "profileUrl": "http://gree.jp/0123457",
                "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
              },
              {
                "nickname": "ナンチョビー・マツダ",
                "profileUrl": "http://gree.jp/0123458",
                "thumbnailUrl": "http://gree.jp/img/0123458.jpg"
              },
              {
                "nickname": "ハコニワ工房",
                "profileUrl": "http://gree.jp/0123459",
                "thumbnailUrl": "http://gree.jp/img/0123459.jpg"
              },
              {
                "nickname": "ハルカ",
                "profileUrl": "http://gree.jp/0123460",
                "thumbnailUrl": "http://gree.jp/img/0123460.jpg"
              }
              ]
             }
        取得できなかった場合:
            {
            "totalResults": 0,
            "itemsPerPage": 0,
            "entry": [],
            "error": True
             }

4. ソーシャル友達のentry情報のみを取得する
   ::
    from gsocial.utils.people import People
    People(request).get_friends_entry(self, userid, has_app=True, fields=None)
    input
        userid: opensocial_owner_id
        has_app: アプリをやっているユーザーを対象にするかどうか defalut:True
        fields: 取得したいフィールド情報(指定しない場合すべての情報を取得する) defalut: None
           ext id,nicknameだけを取る場合
              'id,nickname'
    output
        取得できた場合:
            [
              {
                "nickname": "ナミ",
                "profileUrl": "http://gree.jp/0123457",
                "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
              },
              {
                "nickname": "ナンチョビー・マツダ",
                "profileUrl": "http://gree.jp/0123458",
                "thumbnailUrl": "http://gree.jp/img/0123458.jpg"
              },
              {
                "nickname": "ハコニワ工房",
                "profileUrl": "http://gree.jp/0123459",
                "thumbnailUrl": "http://gree.jp/img/0123459.jpg"
              },
              {
                "nickname": "ハルカ",
                "profileUrl": "http://gree.jp/0123460",
                "thumbnailUrl": "http://gree.jp/img/0123460.jpg"
              }
            ]
        取得できなかった場合:
            []

5. ソーシャル友達の取得するPaginate版
    アプリを利用しているユーザーの友達情報を指定件数分返す
    page,limitを切り替えることでpaginateを実現できる
   ::

    from gsocial.utils.people import People
    People(request).get_friends_entry(self, userid, has_app=True, fields=None)
    input
        userid: opensocial_owner_id
        page: ページ指定 defalut:1
        limit: 取得上限数 defalut:10
        has_app: アプリをやっているユーザーを対象にするかどうか defalut:True
        fields: 取得したいフィールド情報(指定しない場合すべての情報を取得する) defalut: None
           ext id,nicknameだけを取る場合
              'id,nickname'
    output
        取得できた場合:
            [
              {
                "nickname": "ナミ",
                "profileUrl": "http://gree.jp/0123457",
                "thumbnailUrl": "http://gree.jp/img/0123457.jpg"
              },
              {
                "nickname": "ナンチョビー・マツダ",
                "profileUrl": "http://gree.jp/0123458",
                "thumbnailUrl": "http://gree.jp/img/0123458.jpg"
              },
              {
                "nickname": "ハコニワ工房",
                "profileUrl": "http://gree.jp/0123459",
                "thumbnailUrl": "http://gree.jp/img/0123459.jpg"
              },
              {
                "nickname": "ハルカ",
                "profileUrl": "http://gree.jp/0123460",
                "thumbnailUrl": "http://gree.jp/img/0123460.jpg"
              }
            ]
        取得できなかった場合:
            []


6. ユーザーのアプリを利用している友達の数取得
   ::

    from gsocial.utils.people import People
    People(request).get_friends_totalresults(userid)
    input
        userid: opensocial_owner_id
        has_app: アプリをやっているユーザーを対象にするかどうか defalut:True
        fields: 取得したいフィールド情報(指定しない場合すべての情報を取得する) defalut: None
           ext id,nicknameだけを取る場合
              'id,nickname'
    output
        取得できた場合: 人数
        取得できなかった場合: 0

.. _Request:
*Request*

1. Requestのパラメータ生成
   ::

    from gsocial.utils.request import Request
    Request(request).create_request_data(
        title = 'ﾃｽﾄﾘｸｴｽﾄ',
        body = 'ﾎﾞｽが出てきたよ誰か助けて!!',
        callbackurl = コールバックURL,
        mobile_url = フューチャーフォンリンクURL,
        touch_url = スマートフォン用リンクURL,
    )
    input
        下記引数を設定できる
          'title': value,
          'body': value,
          'callbackurl': value,
          'mobile_url': value,
          'touch_url': value,
          'mobile_image': value,
          'touch_image': value,
          'list_type': value,
          'to_user_id': value,
          'editable': value,
          'expire_time': value,
          'backto_url': value,

    output
        引数を設定したもののHashを返す
        ext
        title,body,callbackurl,mobile_url,touch_urlを設定したとすると下記のようなHashがかえってくる
        {
            'title': value,
            'body': value,
            'callbackurl': value,
            'mobile_url': value,
            'touch_url': value,
        }


Templatetags利用方法
---------------------------

.. _ひとことサービス:
*ひとことサービス*

1. ひとことフォームを作る（FP用） ::

    inputd
	callbackurl : ひとことを投稿後に遷移するURL
	body_value : 本文
	submit_value : 送信ボタンの文言
	image_urls_640 : 横640pxサイズの画像URL defalut: None
	image_urls_240 : 横240pxサイズの画像URL defalut: None
	image_urls_75 : 横75pxサイズの画像URL defalut: None

    output
	生成したフォームを返す

    テンプレート側（サンプル）
        {% load hitokoto %}
    	{% get_hitokoto_form callbackurl body_value submit_value image_urls_240 %}

2. ひとことリンクを作る（SP用） ::

    input
	callbackurl : ひとことを投稿後に遷移するURL
	body_value : 本文
	submit_value : 送信ボタンの文言
	image_urls_640 : 横640pxサイズの画像URL defalut: None
	image_urls_240 : 横240pxサイズの画像URL defalut: None
	image_urls_75 : 横75pxサイズの画像URL defalut: None

    output
	生成したリンクを返す

    テンプレート側（サンプル）
        {% load hitokoto %}
	{% get_hitokoto_form_sp callbackurl body_value submit_value image_urls_240 %}


.. _リクエストサービス:
*リクエストサービス*

1. リクエストフォームを作る（FP用）

   リクエストフォームはデザインが絡むため、templatetagsとして利用できません

   サンプルコードとなっていますので、参考にしてください
   ::

    input
	request_users : リクエストを送信したいユーザリスト
		        （to_user_id[]に渡すパラメータ）
	submit_value : 送信ボタンの文言
	title : リクエストのタイトル（必須）
	body : 本文
	callbackurl : リクエストした後に遷移するURL
	mobile_url : リクエストをユーザがクリックした際の飛び先のURL（FP）
	touch_url : リクエストをユーザがクリックした際の飛び先のURL（SP）
	option_params : オプションディクショナリ
             backto_url   : リクエスト送信確認画面からアプリへ戻るためのURL
             mobile_image : メッセージに含める画像のURL（FP）
             touch_image  : メッセージに含める画像のURL（SP）
             list_type    : リクエストの対象となるユーザの種別
             editable     : メッセージをユーザに入力させる
             expire_time  : リクエストが期限切れとなる日時(UTC FORMAT)

    output
	生成したフォームを返す

    テンプレート側（サンプル）
	{% load request %}
	{% get_request_form request_users submit_value title body callbackurl mobile_url touch_url option_params %}

2. リクエストリンクを作る（SP用）

   SP版はリンク生成のみなので、templatetagsとして利用できます
   ::

    input
	request_users : リクエストを送信したいユーザリスト
		        （to_user_id[]に渡すパラメータ）
	submit_value : 送信ボタンの文言
	title : リクエストのタイトル（必須）
	body : 本文
	callbackurl : リクエストした後に遷移するURL
	mobile_url : リクエストをユーザがクリックした際の飛び先のURL（FP）
	touch_url : リクエストをユーザがクリックした際の飛び先のURL（SP）
	option_params : オプションディクショナリ
             backto_url   : リクエスト送信確認画面からアプリへ戻るためのURL
             mobile_image : メッセージに含める画像のURL（FP）
             touch_image  : メッセージに含める画像のURL（SP）
             list_type    : リクエストの対象となるユーザの種別
             editable     : メッセージをユーザに入力させる
             expire_time  : リクエストが期限切れとなる日時(UTC FORMAT)

    output
	生成したリンクを返す

    テンプレート側（サンプル）
	{% load request %}
	{% get_request_form request_users submit_value title body callbackurl mobile_url touch_url option_params %}


.. _Invite Serivice:
*Invite Service*

1. テンプレートタグをロードする
   ::

   {% load gree_service %}

        

2. タグを呼ぶ
   ::

   {% share_service SubmitName callback_url=CallbackUrl message=Message img_url_240=ImgUrl240 %}

        SubmitName: サブミットタグのValue

        CallbackUrl: CallbackURL

        Message: デフォルトメッセージ(119文字制限)

        ImgUrl240: 画像Image
        


.. _Share Serivice:
*Share Service*


1. テンプレートタグをロードする
   ::

   {% load gree_service %}

        

2. タグを呼ぶ
   ::

   {% invite_service SubmitName callback_url=CallbackUrl to_user_ids=ToUserIds message=Message %}

        SubmitName: サブミットタグのValue

        CallbackUrl: CallbackURL

        Message: デフォルトメッセージ(100byte)

        ToUserIds: GreeIDs(Array)
        
