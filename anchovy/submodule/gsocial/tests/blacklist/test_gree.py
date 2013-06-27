# -*- coding: utf-8 -*-
import unittest

from mock import MagicMock
from gsocial.utils.blacklist.gree import BlacklistGree

BLACKLIST = {
    "totalResults": 4,
    "itemsPerPage": 4,
    "startIndex" : 1,
    "entry": [
        {
            "id": 30,
            "ignorelistId" : 101
            },
        {
            "id": 30,
            "ignorelistId" : 102
            },
        {
            "id": 30,
            "ignorelistId" : 103
            },
        {
            "id": 30,
            "ignorelistId" : 104
            }
        ]
    }

BLACKLIST_PERSON = {
    "entry":
        {
        "id": 30,
        "ignorelistId" : 110
        },
    }


class Test_BlacklistGree(unittest.TestCase):

    def test_blacklist_check(self):
        userid = 20000
        target_userid = 110
        BlacklistGree.get_response = MagicMock(return_value=BLACKLIST_PERSON)
        value = BlacklistGree.blacklist_check(userid, target_userid)
        self.assertEqual(value, BLACKLIST_PERSON)
        self.assertEqual(value, False)

if __name__ == '__main__':
    unittest.main()
