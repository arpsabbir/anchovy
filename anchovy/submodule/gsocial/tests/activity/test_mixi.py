# -*- coding: utf-8 -*-
import unittest


class ActivityMixiTests(unittest.TestCase):
    pass

#    def _getTarget(self):
#        from gsocial.utils.activity.mixi import ActivityMixi
#        return ActivityMixi
#
#    def _makeOne(self, *args, **kwargs):
#        return self._getTarget()(*args, **kwargs)
#
#    def test_platform(self):
#        target = self._makeOne()
#        value = target.platform()
#        self.assertEqual(value, 'mixi')
#
#    def test_send(self):
#        target = self._makeOne()
#        value = target.send(userid='10000', title='リクエストテスト')
#        # 上の value には opensocial/utils/base.py の oauth_request() の return値が入る
#        # 下の assert で value に正しい値が入っているか確認する
#        #self.assertEqual(value, )
#
if __name__ == '__main__':
    unittest.main()
