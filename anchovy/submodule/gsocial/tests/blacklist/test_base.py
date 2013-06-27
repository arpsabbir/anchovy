# -*- coding: utf-8 -*-
import unittest

from gsocial.utils.blacklist.base import BlacklistBase

DATA = {
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


class Test_BlacklistBase(unittest.TestCase):

    def test_blacklist_check(self):
        userid = 20000
        target_userid = 30000
        value = BlacklistBase.blacklist_check()
        self.assertEqual(value, None)

if __name__ == '__main__':
    unittest.main()



