# -*- coding: utf-8 -*-
import time


class Loopback:
    # date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    def __init__(self, date=time.strftime('%Y-%m-%d', time.localtime(time.time()))):
        self.date = date
        # print date

if __name__ == '__main__':
    obj = Loopback()
    print obj.date




在外加一层
    # for i in range(8):
    #     if self.df.open[i] - self.df.close[i] >= 0:
    #         yin += 1
    #     else:
    #         yang += 1
    # # 计算箱体和阴阳比例
    # data = self.angle_data(ave=5, stop_dot=8)
    # angle, a, b, model = self.line_model(data)
    # if (yang > yin) and (-30 <= angle <= 30):
    #     # 赋5日均线值
    #     low_offer[index_0] = self.ave_price_5[0]