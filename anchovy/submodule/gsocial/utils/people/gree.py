# -*- coding: utf-8 -*-
"""
People API for Gree
"""
from django.utils import simplejson
from base import PeopleBase
from gsocial.log import Log

LOG_MSG1 = 'Simplejson loads error.'
LOG_MSG2 = 'Simplejson loads type error.'
LOG_MSG3 = 'Simplejson loads with ignore type error.'
LOG_MSG4 = 'Oauth request error.'


class PeopleGree(PeopleBase):
    """
    PeopleAPIを使う（gree用）
    Uses PeopleAPI of Gree.

    プラットフォームからのレスポンス（JSON）のキーに関して
     greeは'entry'キーを利用する
     
     
     Gree uses key name 'entry' to get information from response.
     Example of response:
      
     200 OK
    {
    "totalResults": 1,
    "entry": {
      "id": "0123456",
      "nickname": "グリーアプリ",
      "thumbnailUrl": "http://gree.jp/img/0123456.jpg",
      "gender": "male",
      "age": "20"
     }
   }
   
    """

    def get_myself(self, userid, fields=None, caching=True, cache_update=None):
        """
        アプリを利用しているユーザー本人の情報を取得し、entryキーのバリューを返す
        なければ、Noneを返す

        任意でキャッシュできる（デフォルトではキャッシュする）
        キャッシュを意図的に更新したい場合は、cache_update=Trueとする
        
        From the information of the user,return the values of key name "entry".If there is none,return None.
        You can cache the data(By default,it will be cached).If you want to renew the cache,you can do so by setting cache_update=True.
        
        """
        data = self.get_myself_data(userid, fields, caching, cache_update)
        if data:
            if 'entry' in data:
                return data['entry']
        return None

    def get_friend(self, userid, friend_userid, has_app=True, fields=None):
        """
        アプリを利用しているユーザーのID指定した友達の情報を取得し、entryキーのバリューを返す
        なければ、Noneを返す

        キャッシュはしない
        
        From the information of user`s friend,specified by the user-id,return the values of key name "entry".If there is none,return None.
        
        There is no caching available.
        
        """
        data = self.get_friend_data(userid, friend_userid, has_app, fields)

        if data:
            if 'entry' in data:
                ret = data.get('entry', [])
            else:
                ret = None

        if not ret:
            return None
        return ret[0] if isinstance(ret, (list, tuple)) else ret

    def get_friends(self, userid, has_app=True, fields=None):
        """
        アプリを利用しているユーザーの友達情報を返す

        友達情報を100件毎に取得し、最大1000件（100*10）取得する

        キャッシュはしない
        
        Return the information of user`s friends.
        
        Get 100 friends information each time,and at maximum you could get 1000 information(100*10).
        
        No caching.
        """
        path = '/people/%s/@friends' % userid
        params = {'format': 'json', 'count': '1000'}
        data = None

        # GREEでは最大100件まで指定可能
        params['count'] = 100
        # リクエスト回数デフォルト値（ただし1回目リクエスト時のtotalResultsの値に書き換える）
        range_max = 2
        total_data = None

        if fields:
            params['fields'] = fields
        if has_app:
            params['filterBy'] = 'hasApp'
            params['filterOp'] = 'equals'
            params['filterValue'] = 'true'

        for i in range(range_max):
            params['startIndex'] = params['count'] * i
            res = self.get_response(userid, path, params)

            if res:
                try:
                    data = simplejson.loads(res)
                    # totalResults==0（友達がいない）、もしくは、rangeを超えた時
                    if int(data['totalResults']) == 0 or i >= range_max - 1:
                        data = total_data
                        break
                    else:
                        # for文1回目（total_dataにデータが入っていない時）
                        if not total_data:
                            # 友達数（totalResults）を取得出来るので、range_maxを書き換え
                            range_max = int(data['totalResults']) / 100

                            total_data = data
                            total_data['totalResults'] = int(
                                total_data['totalResults'])
                            total_data['itemsPerPage'] = int(
                                total_data['itemsPerPage'])
                        # for文2回目以降
                        else:
                            total_data['totalResults'] += data['totalResults']
                            total_data['itemsPerPage'] += data['itemsPerPage']
                            total_data['entry'] += data['entry'] # list
                except TypeError:
                    Log.error(LOG_MSG2, [userid, path, res])
                    try:
                        data = simplejson.loads(unicode(res, "utf-8", "ignore"))
                        # totalResults==0（友達がいない）
                        if int(data['totalResults']) == 0:
                            data = total_data
                        else:
                            # for文1回目（total_dataにデータが入っていない時）
                            if not total_data:
                                total_data = data
                                total_data['totalResults'] = int(
                                    total_data['totalResults'])
                                total_data['itemsPerPage'] = int(
                                    total_data['itemsPerPage'])
                            # for文2回目以降
                            else:
                                total_data['totalResults'] += int(
                                    data['totalResults'])
                                total_data['itemsPerPage'] += int(
                                    data['itemsPerPage'])
                                total_data['entry'] += data['entry'] # list
                    except TypeError:
                        Log.error(LOG_MSG3, [userid, path, res])
                        break
                    except Exception:
                        Log.error(LOG_MSG1, [userid, path, res])
                        break
                except Exception:
                    Log.error(LOG_MSG1, [userid, path, res])
                    break
            else:
                Log.error(LOG_MSG4, [userid, path])
                break
        else:
            data = total_data

        if data == None:
            data = {'error': True,
                    'entry': [],
                    'totalResults': '0',
                    'itemsPerPage': '0'
            }

        return data

    def get_friends_totalresults(self, userid, has_app=True, fields=None):
        """
        アプリを利用しているユーザーの全友達の数を返す
        has_appパラメータを指定できる、デフォルトはTrue
        fieldsパラメータを指定できる、デフォルトはNone

        キャッシュはしない
        
        Return the total number of user`s friend.
        You can specify the has_app(True if he or she has already installed the application) parameter.By default it is True.
        You can specity the field parameter.By default it is None.
        
        No caching
        
        """
        friends_data = self.get_friends_page(userid, has_app, fields)
        return friends_data['totalResults']

    def get_friends_entry(self, userid, has_app=True, fields=None):
        """
        アプリを利用しているユーザーの全友達の情報（リスト）を返す
        has_appパラメータを指定できる、デフォルトはTrue
        fieldsパラメータを指定できる、デフォルトはNone

        キャッシュはしない
        
        Return the every information of user`s friend.
        You can specify the has_app(True if he or she has already installed the application) parameter.By default it is True.
        You can specity the field parameter.By default it is None.
        
        No caching
        """
        friends_data = self.get_friends(userid, has_app, fields)
        return friends_data['entry']

    def get_friends_page(self, userid, has_app=True, fields=None, page=1,
                         limit=10):
        """
        アプリを利用しているユーザーの友達情報を指定件数分返す
        件数指定がない場合は10件

        キャッシュはしない
        
        Return specified amount of the user`s friend information.By default,it will return 10 friends information.
        
        No caching.
        """
        path = '/people/%s/@friends' % userid
        params = {'format': 'json'}
        params['count'] = limit
        params['startIndex'] = 1 + limit * (page - 1)
        data = None

        if fields:
            params['fields'] = fields
        if has_app:
            params['filterBy'] = 'hasApp'
            params['filterOp'] = 'equals'
            params['filterValue'] = 'true'

        res = self.get_response(userid, path, params=params)

        if res:
            try:
                data = simplejson.loads(res)
            except TypeError:
                Log.error(LOG_MSG2, [userid, path, res])
                try:
                    data = simplejson.loads(unicode(res, "utf-8", "ignore"))
                except TypeError:
                    Log.error(LOG_MSG3, [userid, path, res])
                except Exception:
                    Log.error(LOG_MSG1, [userid, path, res])
            except Exception:
                Log.error(LOG_MSG1, [userid, path, res])
        else:
            Log.error(LOG_MSG4, [userid, path, res])

        if data == None:
            data = {'error': True,
                    'entry': [],
                    'totalResults': '0',
                    'itemsPerPage': '0',
                    'startIndex': '1'
            }

        return data
