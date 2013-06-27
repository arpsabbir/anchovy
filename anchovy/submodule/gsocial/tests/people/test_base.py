# -*- coding: utf-8 -*-
import unittest

from mock import MagicMock
from gsocial.utils.people.base import PeopleBase

DATA = {
    "totalResults": 1,
    "entry": {
        "id": "0123456",
        "nickname": "SMITH",
        "thumbnailUrl": "http://gree.jp/img/0123456.jpg",
        "gender": "male",
        "age": "20"
        }
    }

DATA_ENTRY = {
    "id": "0123456",
    "nickname": "SMITH",
    "thumbnailUrl": "http://gree.jp/img/0123456.jpg",
    "gender": "male",
    "age": "20"
    }

DATA_FRIENDS = {
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

DATA_FRIENDS_ENTRY = {
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


class PeopleBaseTests(unittest.TestCase):
    """
    simplejsonがローカル環境で通らない
    """
#    def _getTarget(self):
#        from gsocial.utils.people.base import PeopleBase
#        return PeopleBase
#
#    def _makeOne(self, *args, **kwargs):
#        return self._getTarget()(*args, **kwargs)

    def test_get_myself_data(self):
#        target = self._makeOne(request=None)
        target = PeopleBase(request=None)
        target.get_response = MagicMock(return_value=DATA)
        value = target.get_myself_data(userid='0123456', fields=None, caching=False)
        self.assertEqual(value, DATA)

    def test_get_friend_data(self):
        target = PeopleBase(request=None)
        target.get_response = MagicMock(return_value=DATA_FRIENDS)
        value = target.get_friend_data(userid='0123456', friend_userid='20000', has_app=True, fields=None)
        self.assertEqual(value, {'error':True, 'entry':[]})

#    def test_get_friends_data_cache(self):
#        target = PeopleBase(request=None)
#        userid = '10000'
#        value1, value2, value3, value4 = target.get_friends_data_cache(userid,
#                                                                           params={'format':'json'},
#                                                                           has_app=True,
#                                                                           fields=None)
#
#        params = {'filterBy': 'hasApp', 'filterValue': 'true', 'filterOp': 'equals', 'format': 'json'}
#        path = '/people/%s/@friends' % userid
#        cache_key = 'osrequest:%s:%s' % (userid, path)
#
#        self.assertEqual(value1, None)
#        self.assertEqual(value2, params)
#        self.assertEqual(value3, path)
#        self.assertEqual(value4, cache_key)

if __name__ == '__main__':
    unittest.main()
