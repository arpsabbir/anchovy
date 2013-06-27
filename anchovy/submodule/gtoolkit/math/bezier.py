# -*- coding: utf-8 -*-

class Bezier:
    def __init__(self, x1, y1, x2, y2, min_x, max_x, min_y, max_y, eps):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        self._min_x = min_x
        self._max_x = max_x
        self._min_y = min_y
        self._max_y = max_y
        self._eps = eps

    def get(self, x):
        x1 = self._x1
        y1 = self._y1
        x2 = self._x2
        y2 = self._y2
        eps = self._eps

        x = self.fix_x(x)

        # 単純増加する値でないと二分探索できない
        assert 0.0 <= x1 and x1 <= 1.0
        assert 0.0 <= y1 and y1 <= 1.0
        assert 0.0 <= x2 and x2 <= 1.0
        assert 0.0 <= y2 and y2 <= 1.0

        # 目的の値を二分探索する
        down = 0.0
        up = 1.0

        while True:
            t = (down + up) / 2.0
            px = 3*(1-t)*(1-t)*t*x1 + 3*(1-t)*t*t*x2 + t*t*t
            # px が x ± self._eps の範囲内に収まったら抜ける
            if px < x-eps:
                down = t
            elif px > x+eps:
                up = t
            else:
                break

        y = 3*(1-t)*(1-t)*t*y1 + 3*(1-t)*t*t*y2 + t*t*t
        return self.fix_y(y)

    def get_csv(self, step=1.0, output='output.csv'):
        outfile = open(output, 'w')
        x = self._min_x
        while x <= self._max_x:
            print '%f,%f' % (x, self.get(x))
            outfile.write('%f,%f\n' % (x, self.get(x)))
            x = x + step
        outfile.close()

    def fix_x(self, x):
        """
        min_x〜max_xの範囲内にあるxを0.0〜1.0に変換
        """
        if not self._min_x <= x <= self._max_x:
            raise ValueError, 'x is not in range between %f and %f.' % (self._min_x, self._max_x)
        return (x - self._min_x) / (self._max_x - self._min_x)

    def fix_y(self, y):
        """
        0.0〜1.0の範囲内にあるyをmin_y〜max_yに変換
        """
        return round(y * (self._max_y - self._min_y) + self._min_y)
