# -*- coding: utf-8 *-
"""
mobage blacklist api
"""
from base import BlacklistBase
from gsocial.log import Log


class BlacklistMobage(BlacklistBase):
    """
    Ignorelist APIを使う(Mobage用）
    未リファクタ
    """
    def platform(self):
        return 'mobage'

    def is_contain(self, userid, target_userid):
        """
        二者間でのブラックリストチェック
        userid が target_userid をブラックリスト登録してるか？
        """
        path = '/blacklist/%s/@all/%s' % (str(userid), str(target_userid))
            # ブラックリスト登録してない（データがない）と例外 404
        try:
            requestor_id = self.request.osuser.userid
            self.container.oauth_request('GET', requestor_id, path)
            #oauth_request は、例外を出さなくなった
            Log.debug("blacklist2 latest_error_code = %s" % self.latest_error_code);
            if self.latest_error_code == None:
                data = True
                Log.debug('Blacklist True. (None)')
            elif self.latest_error_code == 200:
                data = True
                Log.debug('Blacklist True. (200)')
            elif self.latest_error_code == 404:
                data = False
                Log.debug('Blacklist False.(404)')
            else:
                data = False
                Log.error('blacklist2 unexpected error code.')
        except:
            data = False
            Log.debug('Blacklist False. (except)')
        return data
