# -*- coding: utf-8 -*-
"""
リクエストサービス サンプルコード

<< --注意-- >>
On FP-version
As FP-version need the whole form with pictures or images you have to
custmoize the following source cord.We leave that job to you as the each
designs of form  will be quite diffent.

On SP-version
The templatetags will provide the links.
As the SP-version only needs to create the link,
you can use this cord as the templatetags.

*A sample for the template
{% get_request_form request_users=player_friends_list submit_value="sendrequest" title="testtitle" body="bossisstrong" callbackurl=callbackurl mobile_url=mobile_url touch_url=touch_url option_params=option_params %}
{% get_request_form player_friends_list "sendrequest" "testtitle" "bossisstrong" callbackurl mobile_url touch_url option_params %}

　FP版について
　FP版では画像などを含むフォームを生成する必要がありますが、フォームのデザインは
 各場合によって著しく異なりますので共通化はしていません。
 下記のコードを参考にご自身のtemplatetagsをお書き下さい。

SP版について
 templatetagsでリンクを提供しています
 SP版はリンク生成のみなので、templatetagsとして利用できます
<< -------- >>

* テンプレートでは以下のように使う
例
{% get_request_form request_users=player_friends_list submit_value="ﾘｸｴｽﾄを送信する" title="ﾃｽﾄﾀｲﾄﾙ" body="ボスが強いよ" callbackurl=callbackurl mobile_url=mobile_url touch_url=touch_url option_params=option_params %}
{% get_request_form player_friends_list "ﾘｸｴｽﾄを送信する" "ﾃｽﾄﾀｲﾄﾙ" "ボスが強いよ" callbackurl mobile_url touch_url option_params %}
"""
import os
import urllib

from django import template

from gsocial.log import Log

register = template.Library()
abs_path = os.path.dirname(os.path.abspath(__file__))
file_path = abs_path + '/../templates/opensocial/request.html'
file_path_sp = abs_path + '/../templates/opensocial/request_sp.html'


@register.inclusion_tag(file_path)
def get_request_form( request_users,
                      submit_value,
                      title,
                      body,
                      callbackurl,
                      mobile_url,
                      touch_url,
                      option_params={} ):
    u"""
    リクエストサービスのフォームを生成し、返す
    フィーチャーフォン版

    外部テンプレート: gsocial/templates/opensocial/request.html

    使い方::

        {% get_request_form <request_users> <submit_value> <title> <body> <callbackurl> <mobile_url> <touch_url> <option_params> %}

    引数:

        :request_users: リクエストを送信したいユーザリスト
                       （to_user_id[]に渡すパラメータ）
        :submit_value: 送信ボタンの文言
        :title: リクエストのタイトル（必須）
        :body: 本文
        :callbackurl: リクエストした後に遷移するURL
        :mobile_url: リクエストをユーザがクリックした際の飛び先のURL（FP）
        :touch_url: リクエストをユーザがクリックした際の飛び先のURL（SP）
        :option_params: オプションディクショナリ

    option_params:

        :backto_url: リクエスト送信確認画面からアプリへ戻るためのURL
        :mobile_image: メッセージに含める画像のURL（FP）
        :touch_image: メッセージに含める画像のURL（SP）
        :list_type: リクエストの対象となるユーザの種別
        :editable: メッセージをユーザに入力させる
        :expire_time: リクエストが期限切れとなる日時(UTC FORMAT)

    Create the form for the request service and return it.(For FP)

    Customize the following source cord with your own designs of the forms.

    Arguments:

        :request_users: A Userlist whom you want to send request.(A parameter to be handed to to_user_id[])
        :submit_value: A letter on submit botton
        :title: The title of request(indispensable)
        :body: Message
        :callbackurl: A URL which will be redirected after the request.
        :mobile_url: A URL which will be redirected after the click(FP).
        :touch_url: A URL which will be redirected after the click(SP).
        :option_params: a optional dictionary

    option_params:

        :backto_url: A URL of the application from the "request sent confirmation"screen
        :mobile_image: URL of the image which will be contain in the message（FP）
        :touch_image: URL of the image which will be contain in the message（SP）
        :list_type: The type of subjected users.
        :editable: Whether User is allowed to edit or not.
        :expire_time: The expire date of the request(UTC FORMAT)

    """
    # checks the content of option_params
    # option_paramsの中身をチェック
    # TODO : もっと綺麗にしたい
    keys = option_params.keys()
    backto_url = option_params['backto_url'] if 'backto_url' in keys else None
    mobile_image = option_params['mobile_image'] if 'mobile_image' in keys else None
    touch_image = option_params['touch_image'] if 'touch_image' in keys else None
    list_type = option_params['list_type'] if 'list_type' in keys else None
    editable = option_params['editable'] if 'editable' in keys else None
    expire_time = option_params['expire_time'] if 'expire_time' in keys else None

    # title is indispensable,so check.
    # titleは必須のため、チェック
    if not title:
        Log.error('title is empty.', body)
        raise

    # if list_type was not setted,use "specified"
    # list_typeの指定が無かった場合、specifiedを指定する
    if list_type == None:
        list_type = 'specified'

    # body is indispensable when editable is True,so check
    # bodyはeditableがtrueでない場合は必須のため、チェック
    # TODO : editable==Trueの場合、メッセージをユーザに入力させる
    # そのため、フォーム生成のhtml側で、入力フォームを生成する必要がある
    if editable != True:
        if body == None:
            Log.error('body is empty.', body)
            raise

    if request_users:
        temp = []
        for user in request_users:
            user_params = {}
            user_params['id'] = user['id'] if 'id' in user else None
            user_params['nickname'] = user['nickname'] if 'nickname' in user else None
            user_params['thumbnail'] = user['thumbnail'] if 'thumbnail' in user else None
            temp.append(user_params)

    return {
        'request_users': temp,
        'submit_value': submit_value,

        'title': title,
        'body': body,
        'callbackurl': callbackurl,
        'mobile_url': mobile_url,
        'touch_url': touch_url,

        'backto_url': backto_url,
        'mobile_image': mobile_image,
        'touch_image': touch_image,
        'list_type': list_type,
        'editable': editable,
        'expire_time': expire_time,
        }


@register.inclusion_tag(file_path_sp)
def get_request_form_sp( request_users,
                         submit_value,
                         title,
                         body,
                         callbackurl,
                         mobile_url,
                         touch_url,
                         option_params={} ):
    u"""
    リクエストサービスのリンクを作成し、返す
    スマートフォン版

    外部テンプレート: gsocial/templates/opensocial/request_sp.html

    使い方::

        {% get_request_form <request_users> <submit_value> <title> <body> <callbackurl> <mobile_url> <touch_url> <option_params> %}

    引数:

        :request_users: リクエストを送信したいユーザリスト
                    （to_user_id[]に渡すパラメータ）
        :submit_value: 送信ボタンの文言
        :title: リクエストのタイトル（必須）
        :body: 本文
        :callbackurl: リクエストした後に遷移するURL
        :mobile_url: リクエストをユーザがクリックした際の飛び先のURL（FP）
        :touch_url: リクエストをユーザがクリックした際の飛び先のURL（SP）
        :option_params: オプションディクショナリ

    option_params:

        :backto_url: リクエスト送信確認画面からアプリへ戻るためのURL
        :mobile_image: メッセージに含める画像のURL（FP）
        :touch_image: メッセージに含める画像のURL（SP）
        :list_type: リクエストの対象となるユーザの種別
        :editable: メッセージをユーザに入力させる
        :expire_time: リクエストが期限切れとなる日時(UTC FORMAT)

    Create the link for the request service and return it.(For SP)

    Arguments:

        :request_users: A Userlist whom you want to send request.(A parameter to be handed to to_user_id[])
        :submit_value: A letter on submit botton
        :title: The title of request(indispensable)
        :body: Message
        :callbackurl: A URL which will be redirected after the request.
        :mobile_url: A URL which will be redirected after the click(FP).
        :touch_url: A URL which will be redirected after the click(SP).
        :option_params: a optional dictionary

    option_params:

         :backto_url: A URL of the application from the "request sent confirmation"screen
         :mobile_image: URL of the image which will be contain in the message（FP）
         :touch_image: URL of the image which will be contain in the message（SP）
         :list_type: The type of subjected users.
         :editable: Whether User is allowed to edit or not.
         :expire_time: The expire date of the request(UTC FORMAT)
    """
    # check the content of option_params
    # option_paramsの中身をチェック
    # TODO : もっと綺麗にしたい
    keys = option_params.keys()
    backto_url = option_params['backto_url'] if 'backto_url' in keys else None
    mobile_image = option_params['mobile_image'] if 'mobile_image' in keys else None
    touch_image = option_params['touch_image'] if 'touch_image' in keys else None
    list_type = option_params['list_type'] if 'list_type' in keys else None
    editable = option_params['editable'] if 'editable' in keys else None
    expire_time = option_params['expire_time'] if 'expire_time' in keys else None

    # title is indispensable ,so check
    # titleは必須のため、チェック
    if not title:
        Log.error('title is empty.', body)
        raise

    # if list_type was not setted ,use "specified"
    # list_typeの指定が無かった場合、specifiedを指定する
    if list_type == None:
        list_type = 'specified'

    # if editable is True body is indispensable,so check
    # bodyはeditableがtrueでない場合は必須のため、チェック
    # TODO : editable==Trueの場合、メッセージをユーザに入力させる
    # そのため、フォーム生成のhtml側で、入力フォームを生成する必要がある
    if editable != True:
        if body == None:
            Log.error('body is empty.', body)
            raise

    # encode
    # エンコードする
    callbackurl = urllib.quote(callbackurl)

    # create a parameter to be handed to user_to_id
    # user_to_idに渡すパラメータを生成
    request_user_ids_str = ','.join(request_users)

    return {
        'request_users': request_user_ids_str,
        'submit_value': submit_value,

        'title': title,
        'body': body,
        'callbackurl': callbackurl,
        'mobile_url': mobile_url,
        'touch_url': touch_url,

        'backto_url': backto_url,
        'mobile_image': mobile_image,
        'touch_image': touch_image,
        'list_type': list_type,
        'editable': editable,
        'expire_time': expire_time,
        }
