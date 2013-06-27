# -*- coding: utf-8 -*-

from math import exp, log

class GraphType(object):
    def __init__(self, k, min_x, max_x, min_y, max_y):
        self.k = k 
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def get(self, x):
        raise NotImplementedError, 'GraphType.get'

    def get_csv(self, step=1.0, output='output.csv'):
        outfile = open(output, 'w')
        x = self.min_x
        while x <= self.max_x:
            print '%f,%f' % (x, self.get(x))
            outfile.write('%f,%f\n' % (x, self.get(x)))
            x = x + step
        outfile.close()

    def fix_x(self, x):
        """
        min_x〜max_xの範囲内にあるxを0.0〜1.0に変換
        """
        if not self.min_x <= x <= self.max_x:
            raise ValueError, 'x is not in range between %f and %f.' % (self.min_x, self.max_x)
        return (x - self.min_x) / (self.max_x - self.min_x)

    def fix_y(self, y):
        """
        0.0〜1.0の範囲内にあるyをmin_y〜max_yに変換
        """
        return round(y * (self.max_y - self.min_y) + self.min_y)


class GraphType1(GraphType):
    def get(self, x):
        x = self.fix_x(x)
        y = x
        return self.fix_y(y)


class GraphType2(GraphType):
    def get(self, x):
        x = self.fix_x(x)
        y = (exp(self.k * x) - 1) / (exp(self.k) - 1)
        return self.fix_y(y)


class GraphType3(GraphType):
    def get(self, x):
        x = self.fix_x(x)
        y = 1.0 / self.k * log(x * (exp(self.k) - 1) + 1)
        return self.fix_y(y)


class GraphType4(GraphType):
    def get(self, x):
        x = self.fix_x(x) * 2
        if x < 1.0:
            y = (exp(self.k * x) - 1) / (exp(self.k) - 1) / 2
        else:
            x = x - 1.0
            y = 1.0 / self.k * log(x * (exp(self.k) - 1) + 1) / 2 + 0.5
        return self.fix_y(y)


class GraphType5(GraphType):
    def get(self, x):
        x = self.fix_x(x) * 2
        if x < 1.0:
            y = 1.0 / self.k * log(x * (exp(self.k) - 1) + 1) / 2
        else:
            x = x - 1.0
            y = (exp(self.k * x) - 1) / (exp(self.k) - 1) / 2 + 0.5
        return self.fix_y(y)
