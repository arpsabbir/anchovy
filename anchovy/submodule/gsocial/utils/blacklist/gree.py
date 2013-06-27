# -*- coding: utf-8 *-
"""
Blacklist API(Ignorelist API) for GREE
"""
from django.utils import simplejson

from gsocial.log import Log

from gsocial.set_container import Container
from gsocial.utils.base import GsocialCache
from base import BlacklistBase


class BlacklistGree(BlacklistBase):
    """
    IgnorelistAPIを使う(GREE用）
    Use IgnorelistAPI of Gree
    """
    def blacklist_check(self, userid, target_userid, caching=False, cache_update=None):
        """
        二者間でのブラックリストチェック
        userid が target_userid をブラックリスト登録してるか？
        任意でキャッシュできる（デフォルトではキャッシュしない）
        （GREE規約上、ブラックリストは24時間キャッシュできるようだが、しない）

        引数
         userid
         target_userid
         caching
         cache_update

        返り値
         is_data : Trueなら、ブラックリストに登録している
                   Falseなら、ブラックリストに登録されていない

        
        "Blacklist checking" between the two persons:whether the "userid"
        has registered "target_userid" for blacklist?
        You can cache it if you want(but by default you can`t cache it)
    
        arguments
         userid
         target_userid
         caching
         cache_update

        return value
         is_data : if True,registerd on blacklist
                   if False,not registerd on blacklist
        
        """
        from django.conf import settings

        if settings.OPENSOCIAL_DEBUG:
            return False
        #requestor_id = self.container.request.osuser.userid


        path = '/ignorelist/%s/@all/%s/' % (str(userid), str(target_userid))
        cache_key = path
        data = []

        # test
        #cache_update = True

        if caching and cache_update == False:
            is_data = GsocialCache.get_cache(cache_key)
            #print 'cache', is_data
            if is_data != None:
                return is_data

        for retry_count in xrange(self.RETRY_COUNT):
            try:
                res = self.get_response(userid, path)
                #res = self.get_response(requestor_id, path)
                data = simplejson.loads(res)
                break
            except TypeError:
                Log.warn('Blacklist: response type error. retry:%s' % retry_count)
                continue
            except Exception:
                Log.warn('Blacklist: response error. retry:%s' % retry_count)
                continue

        Log.debug(data)
        if not data:
            Log.error("Blacklist: not data.")
            raise self.container.ResponseError('Blacklist API','Get ignorelist (gree).')

        if 'entry' in data and data['entry']:
            is_data = True
        else:
            is_data = False

        #print 'no cache', is_data
        if caching:
            GsocialCache.set_cache(cache_key, is_data)
        return is_data
