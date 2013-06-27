# -*- coding: utf-8 -*-
"""
People API
Define the methods which will be commonly used in every platform.
"""
from django.utils import simplejson

from gsocial.set_container import Container
from gsocial.utils.base import GsocialCache
from gsocial.log import Log

class PeopleBase(object):
    """
    Base class of People API
    """

    # ロギング用メッセージ
    LOG_MSG1 = 'Simplejson loads error.'
    LOG_MSG2 = 'Simplejson loads type error.'
    LOG_MSG3 = 'Simplejson loads with ignore type error.'
    LOG_MSG4 = 'Oauth request error.'

    def __init__(self, request):
        # OpenSocialのContainerを作成する
        self.container = Container(request)

    def get_response(self, userid, path, params):
        """
         Request to the platform,and return it response.
         Return value would be on JSON-format.Does not return the response code.
        """
        return self.container.oauth_request('GET', userid, path, params=params)

    def get_myself_data(self, userid, fields=None, caching=True, cache_update=None):
        
        """
        アプリを利用しているユーザー本人の情報を取得する
        任意でキャッシュできる（デフォルトではキャッシュする）
        
        Get the information of user.
        You can use caching(default will do it)
        """
        
        path = '/people/%s/@self' % userid
        cache_key = path
        data = None

        if caching:
            data = GsocialCache.get_cache(cache_key)
            #print 'cache:', data

        # dataが空の時、もしくは、キャッシュを更新したい時
        if data == None or cache_update == True:
            #print 'not cache:', data
            #print 'cache_update:', cache_update
            params = {}
            if fields:
                params['fields'] = fields
            res = self.get_response(userid, path, params)

            Log.debug('Debug.', res)

            if res:
                try:
                    data = simplejson.loads(res)
                    if caching:
                        GsocialCache.set_cache(cache_key, data)
                except TypeError:
                    Log.error(self.LOG_MSG2, [userid, path, res])
                    try:
                        data = simplejson.loads(unicode(res, "utf-8", "ignore"))
                        if caching:
                            GsocialCache.set_cache(cache_key, data)
                    except TypeError:
                        data = None
                        Log.error(self.LOG_MSG3, [userid, path, res])
                    except Exception:
                        data = None
                        Log.error(self.LOG_MSG1, [userid, path, res])
                except Exception:
                    data = None
                    Log.error(self.LOG_MSG1, [userid, path, res])
            else:
                data = None
                Log.error(self.LOG_MSG4, [userid, path])

        return data

    def get_friend_data(self, userid, friend_userid, has_app=True, fields=None):
        """
        アプリを利用しているユーザーのID指定した友達の情報を取得する
         
        キャッシュはしない
        
        Get the information of user`s friend with specified ID.
        
        No caching.
        """
        path = '/people/%s/@friends/%s' % (userid, friend_userid)
        params = {'format' : 'json'}

        if fields:
            params['fields'] = fields
        if has_app:
            params['filterBy'] = 'hasApp'

        res = self.get_response(userid, path, params)
        if res:
            try:
                data = simplejson.loads(res)
            except TypeError:
                Log.error(self.LOG_MSG2, [userid, path, res])
                try:
                    data = simplejson.loads(unicode(res, "utf-8", "ignore"))
                except TypeError:
                    data = None
                    Log.error(self.LOG_MSG3, [userid, path, res])
                except Exception:
                    data = None
                    Log.error(self.LOG_MSG1, [userid, path, res])
            except Exception:
                data = None
                Log.error(self.LOG_MSG1, [userid, path, res])
        else:
            Log.error(self.LOG_MSG4, [userid, path, res])
            data = {'error':True, 'entry':[]}

        Log.debug('Check data for debug.', [userid, data])
        return data
