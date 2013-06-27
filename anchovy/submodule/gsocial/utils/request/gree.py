# -*- coding: utf-8 -*-
"""
Request API GREE用

Request API for Gree
"""
#import cgi
from base import RequestBase


class RequestGree(RequestBase):
    """
    PeopleAPIを使う（gree用）
    
    Use peopleAPI of Gree
    """

#    TEMPLATE = u'''<form action="request:friend" method="post">
#    %(parts)s
#        <input type="submit" value="%(submit_title)s" />
#    </form>
#    '''
#
#    TEMPLATE_PARTS = u'''
#    <input type="hidden" name="%(paramname)s" value="%(value)s" />
#    '''
#
    PARAMETERS = set([
            'title',
            'body',
            'callbackurl',
            'mobile_url',
            'touch_url',
            'mobile_image',
            'touch_image',
            'list_type',
            'to_user_id',
            'editable',
            'expire_time',
            'backto_url',
            ])

    def create_request_data(self, **argv):
        """
        実際のリクエスト処理
        Processing the request.
        """
        ret = {}
        for k,v in argv.iteritems():
            if k not in self.PARAMETERS:
                raise RequestServiceError('Invalid argment (%s)' % k)
            ret[k] = v

        if not ret.get('title', ''):
            raise RequestServiceError('required title')

        if not ret.get('editable', False) and not ret.get('body', ''):
            raise RequestServiceError('required body')

        #print 'ret',ret
        return ret


