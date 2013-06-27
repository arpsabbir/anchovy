# -*- coding: utf-8 -*-
"""
auth device for gree
"""
from base import AuthAPI
from gsocial.utils.people.gree import PeopleGree


class AuthAPIGree(AuthAPI):
    '''
    端末認証 (GREE用)
    '''
    def _get_auth_id(self, userid):
        '''
        APIによる 識別ID取得
        '''
        auth_id = None
        profile = PeopleGree(self.request).get_myself(userid, 'userHash', caching=False)
        if profile:
            if 'userHash' in profile and profile['userHash']:
                auth_id = profile['userHash']

        return auth_id

    def _get_auth(self, userid):
        """
        APIによる 識別ID/userGrade取得
        """
        auth_id = None
        user_grade = None
        profile = PeopleGree(self.request).get_myself(userid, 'userHash,userGrade', caching=False)
        if profile:
            if 'userHash' in profile and profile['userHash']:
                auth_id = profile['userHash']
            if 'userGrade' in profile and profile['userGrade']:
                user_grade = profile['userGrade']

        return [auth_id, user_grade]

