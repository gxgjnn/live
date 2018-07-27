# -*- coding: utf-8 -*-

import math
import pandas as pd
from STOCK_CHOOSE.stock_box import Calculation
from deal import Deal
import time
from utils import create_data


class Strategy(Calculation):
    """
    def selling():situation3-7中，卖出数量不到200的按200算，200为可调参数
    """

    def __init__(self, stock_id):
        super(Calculation, self).__init__(stock_id)

    def buying(self):
        global running_box
        # 支撑线压力线，波谷波峰数据集，变异系数，支撑点压力点，以及原因的获取
        # df_s, cv_s, price_s = self.support_line()
        e_support, reason_s = self.support_dot()
        # df_p, cv_p, price_p = self.pressure_line()
        e_pressure, reason_p = self.pressure_dot()
        obj1 = Deal(self.stock_id)

        price_buy = 0
        price_sell = 0
        cash = 0
        num = 0
        if self.df.high[0] < self.ave_price_60[0]:
            # 上
            if self.df.low[0] >= e_support:
                tik_tok = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                waiting_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/waiting_box.csv')
                waiting_detail = pd.DataFrame([[tik_tok, self.stock_id, num, price_buy, price_sell]],
                                              columns=['drop_time', 'stock_id', 'num', 'price_buy', 'price_sell'],
                                              index=[0])
                waiting_box = pd.concat([waiting_box, waiting_detail], axis=0)
                waiting_box.to_csv('waiting_box.csv', encoding='utf-8', index_label=False, mode='w')

            # 中
            elif self.df.low[0] <= e_support <= self.df.high[0]:
                price_buy = e_support
                price_sell = 0
                cash = obj1.pocket()
                num = math.floor(cash / (price_buy * 100)) * 100
                if num >= 100:
                    print 'situation1'
                    return price_buy, price_sell, cash, num

            # 下
            else:
                research_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/research_box.csv')
                tik_tok = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                stock_id = self.stock_id
                explain = 'situation2'
                research_detail = pd.DataFrame([[tik_tok, stock_id, explain]],
                                               columns=['drop_time', 'stock_id', 'explain'], index=[0])
                research_box = pd.concat([research_box, research_detail], axis=0)
                research_box.to_csv('research_box.csv', encoding='utf-8', index_label=False, mode='a')

        else:
            waiting_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/waiting_box.csv')
            price_buy = waiting_box.loc[waiting_box.stock_id == self.stock_id, 'price_buy'][0]
            # whatever cv_p == 1 or not ,跳空位必须在e_pressure下
            # 跳空保存
            if (self.df.low[0] > self.ave_price_5[0]) and (self.df.high[0] < e_pressure):
                price_buy = self.ave_price_5[0]
                price_sell = 0
                # num是无需在意的值
                num = 0
                tik_tok = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                waiting_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/waiting_box.csv')
                waiting_detail = pd.DataFrame([[tik_tok, self.stock_id, num, price_buy, price_sell]],
                                              columns=['drop_time', 'stock_id', 'num', 'price_buy', 'price_sell'],
                                              index=[0])
                waiting_box = pd.concat([waiting_box, waiting_detail], axis=0)
                waiting_box.to_csv('waiting_box.csv', encoding='utf-8', index_label=False, mode='w')

            # 中
            elif (self.df.low[0] <= price_buy <= self.df.high[0]) and (self.df.high[0] < e_pressure):
                cash = obj1.pocket()/5
                num = math.floor(cash / (price_buy * 100)) * 100
                if num >= 100:
                    print 'situation3'
                    return price_buy, price_sell, cash, num

        return price_buy, price_sell, cash, num

    def selling(self):
        global running_box
        # 支撑线压力线，波谷波峰数据集，变异系数，支撑点压力点，以及原因的获取
        # df_s, cv_s, price_s = self.support_line()
        e_support, reason_s = self.support_dot()
        # df_p, cv_p, price_p = self.pressure_line()
        e_pressure, reason_p = self.pressure_dot()
        obj1 = Deal(self.stock_id)

        price_buy = 0
        price_sell = 0
        cash = 0
        num = 0
        # 涨停止盈
        if self.df.low[0] <= self.df.close[1] * 1.09 <= self.df.high[0]:
            price_buy = 0
            price_sell = self.df.close[1] * 1.09
            num0 = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0] / 5
            num = math.floor(num0 * 100) * 100
            commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001, open_commission=0.0003,
                                                              close_commission=0.0003, min_commission=5)
            cash = num * price_sell - commission_sell
            if num >= 200:
                print 'situation4'
                return price_buy, price_sell, cash, num
            else:
                num = 200
                commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                  open_commission=0.0003, close_commission=0.0003,
                                                                  min_commission=5)
                cash = num * price_sell - commission_sell
                print 'situation5'
                return price_buy, price_sell, cash, num

        # 长上影线止盈
        close_ave5 = create_data.ave_data_create(self.df.close, 5)
        open_ave5 = create_data.ave_data_create(self.df.open, 5)
        high_ave5 = create_data.ave_data_create(self.df.high, 5)
        low_ave5 = create_data.ave_data_create(self.df.low, 5)
        if ((self.df.high[0] - max(self.df.close[0], self.df.open[0])) / (self.df.high[0] - self.df.low[0]) >= 0.5) or \
                ((high_ave5[0] - max(open_ave5[0], close_ave5[0])) / (high_ave5[0] - low_ave5[0]) >= 0.5):
            if self.df.volume[0] > self.df.volums[0:5].mean():
                price_buy = 0
                price_sell = self.df.close[0]
                num0 = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0] / 5
                num = math.floor(num0 * 100) * 100
                commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                  open_commission=0.0003, close_commission=0.0003,
                                                                  min_commission=5)
                cash = num * price_sell - commission_sell
                if num >= 200:
                    print 'situation6'
                    return price_buy, price_sell, cash, num
                else:
                    num = 200
                    commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                      open_commission=0.0003, close_commission=0.0003,
                                                                      min_commission=5)
                    cash = num * price_sell - commission_sell
                    print 'situation7'
                    return price_buy, price_sell, cash, num

        if self.df.high[0] < self.ave_price_60[0]:
            # 支撑位止损
            if self.df.close[0] <= e_support:
                price_sell = self.df.close[0]
                num = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0]
                commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                  open_commission=0.0003, close_commission=0.0003,
                                                                  min_commission=5)
                cash = num * price_sell - commission_sell
                print 'situation8'
                return price_buy, price_sell, cash, num
        else:
            # 跳空止盈
            if self.df.low[0] > self.ave_price_5[0]:
                price_buy = 0
                price_sell = self.df.close[0]
                num0 = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0] / 5
                num = math.floor(num0 * 100) * 100
                commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                  open_commission=0.0003, close_commission=0.0003,
                                                                  min_commission=5)
                cash = num * price_sell - commission_sell
                if num >= 200:
                    print 'situation9'
                    return price_buy, price_sell, cash, num
                else:
                    num = 200
                    commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                      open_commission=0.0003, close_commission=0.0003,
                                                                      min_commission=5)
                    cash = num * price_sell - commission_sell
                    print 'situation10'
                    return price_buy, price_sell, cash, num
            # 超过压力位止盈
            # 对于cv_p没做限定，如果存在负角度的压力线，是否会低于60日线,已改pressure角度0到30
            elif self.df.low[0] <= e_pressure <= self.df.high[0]:
                price_buy = 0
                price_sell = self.df.close[0]
                num0 = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0] / 5
                num = math.floor(num0 * 100) * 100
                commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                  open_commission=0.0003, close_commission=0.0003,
                                                                  min_commission=5)
                cash = num * price_sell - commission_sell
                if num >= 200:
                    print 'situation11'
                    return price_buy, price_sell, cash, num
                else:
                    num = 200
                    commission_buy, commission_sell = obj1.order_cost(num, price_sell, close_tax=0.001,
                                                                      open_commission=0.0003, close_commission=0.0003,
                                                                      min_commission=5)
                    cash = num * price_sell - commission_sell
                    print 'situation12'
                    return price_buy, price_sell, cash, num

        return price_buy, price_sell, cash, num

if __name__ == "__main__":
    pass