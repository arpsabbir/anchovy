# -*- coding: utf-8 -*-

import unittest
import random

from gtoolkit.math import parameter_factory, bezier_factory


class TestMath(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testGraph(self):
        for graph_type in xrange(1, 6):
            for n in range(10):
                k = random.randint(1, 20)
                min_x = random.randint(1, 10)
                max_x = random.randint(11, 100)
                min_y = random.randint(0, 10)
                max_y = random.randint(11, 100)
                param = parameter_factory(graph_type, k, min_x, max_x, min_y, max_y)
                current = param.min_y
                self.failUnless(param.get(min_x) == float(min_y), 'f(min_x) does not match min_y.')
                self.failUnless(param.get(max_x) == float(max_y), 'f(max_x) does not match max_y.')
                for x in xrange(int(param.min_x), int(param.max_x) + 1):
                    self.failUnless(param.get(x) >= current, 'Parameter decreased! (%d -> %d)' % (current, param.get(x)))
                    current = param.get(x)

    def testBezier(self):
        for n in range(15):
            x1 = random.random()
            x2 = random.random()
            y1 = random.random()
            y2 = random.random()
            min_x = random.randint(1, 10)
            max_x = random.randint(11, 100)
            min_y = random.randint(0, 10)
            max_y = random.randint(11, 100)
            param = bezier_factory(x1, y1, x2, y2, min_x, max_x, min_y, max_y)
            current = param._min_y
            for x in xrange(int(param._min_x), int(param._max_x + 1)):
                self.failUnless(param.get(x) >= current, 'Parameter decreased! (%d -> %d)' % (current, param.get(x)))
                current = param.get(x)


if __name__ == '__main__':
    unittest.main()
