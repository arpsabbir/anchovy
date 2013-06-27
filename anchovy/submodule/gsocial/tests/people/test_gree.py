# -*- coding: utf-8 -*-
import unittest

from gsocial.utils.people.gree import PeopleGree

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
#        from gsocial.utils.people.gree import PeopleGree
#        return PeopleGree
#
#    def _makeOne(self, *args, **kwargs):
#        return self._getTarget()(*args, **kwargs)

    def test_get_myself(self):
#        target = self._makeOne()
        target = PeopleGree(request=None)
        value = target.get_myself(userid='0123456')
        self.assertEqual(value, DATA_ENTRY)

#    def test_get_friend(self):
#        target = self._makeOne()
#        value = target.get_friend(userid='0123456', friend_userid='0123457')
#        self.assertEqual(value, DATA_FRIENDS_ENTRY)
#
#    def test_get_friends(self):
#        target = self._makeOne()
#        value = target.get_friends(userid='0123456')
#        self.assertEqual(value, None)
#
#    def test_get_friends_page(self):
#        target = self._makeOne()
#        value = target.get_friends_page(userid='0123456', has_app=True, fields=None, page=1, limit=10)
#        self.assertEqual(value, None)

if __name__ == '__main__':
    unittest.main()
