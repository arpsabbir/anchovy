# -*- coding: utf-8 -*-
import unittest


class ActivityGreeTests(unittest.TestCase):

    def _getTarget(self):
        from gsocial.utils.activity.gree import ActivityGree
        return ActivityGree

    def _makeOne(self, *args, **kwargs):
        return self._getTarget()(*args, **kwargs)

#    def test_platform(self):
#        target = self._makeOne()
#        value = target.platform()
#        self.assertEqual(value, 'gree')

    def test_send(self):
        target = self._makeOne()
        value = target.send(userid='10000', title='リクエストテスト')
        #"value" will receive the return value of oauth_request() of opensocial/utils/base.py 
        # 上の value には opensocial/utils/base.py の oauth_request() の return値が入る
        # 下の assert で value に正しい値が入っているか確認する
        #self.assertEqual(value, )

if __name__ == '__main__':
    unittest.main()
