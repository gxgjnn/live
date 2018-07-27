# -*- coding: utf-8 -*-

# 每天都要数据更新，重新计算
# 对计算的值会产生变化，一旦变化，记录并警报，哪些变化需要更新，哪些不需要
import pandas as pd
from STOCK_CHOOSE.line import Line
from utils import data_process
import numpy as np


class Calculation(Line):
    """
    def stocks_choose():long_up_shadow中参数60，因为目前60均线长度只有150(见create_data.py),该参数为可调参数，不能超过150
                        angle当前为(0,45),为可调参数
                        len(long_up_shadow),当前为2，为可调参数
                        data0.close[:60]为0的是停牌时间不超过5天，参数当前为5，60和5都是可调参数
                        len(list(data0.close[:135].loc[data0.close == 0]))<=15:...........135,15都是可调参数
    
    """
    def __init__(self, stock_id, stock_box):
        super(Line, self).__init__(stock_id)
        self.stock_box = stock_box

    def support_dot(self):
        """
        
        :return: 支撑点，说明，前期测试只取存在支撑线的情况
        """
        # 支撑位线的DataFrame, 变异系数，支撑线最新拟合价格
        df_s, cv_s, price_s, stop_dot_s = self.support_line()
        e_support = 0
        reason = 'has no support'
        # 存在波谷拟合线且存在支撑线
        if cv_s == 1:
            e_support = price_s
            reason = 'has support'

        # 存在波谷拟合线不存在支撑线
        elif price_s != 0:
            e_support = price_s
        return e_support, reason

    def pressure_dot(self):
        """
        
        :return: 压力点，说明，前期测试只取存压力线的情况
        """
        # 压力位线的DataFrame, 变异系数，支撑线最新拟合价格
        df_p, cv_p, price_p, stop_dot_p = self.pressure_line()
        e_pressure = 0
        reason = 'has no pressure'
        # 存在波峰拟合线且存在压力线
        if cv_p == 1:
            e_pressure = price_p
            reason = 'has pressure'
        # 存在波峰拟合线不存在压力线
        elif price_p != 0:
            e_pressure = price_p
        return e_pressure, reason

    def stocks_choose(self):
        data0 = data_process.Get_DataFrame_0(self.stock_id, self.date)
        # long_up_shadow长上影线序列列表
        long_up_shadow = []
        if len(list(data0.close[:150].loc[data0.close == 0])) <= 30:
            for i in range(60):
                if self.df.close[i] > self.ave_price_60[i]:
                    if ((self.df.high[i] - max(self.df.close[i], self.df.open[i])) > (
                                self.df.high[i] - self.df.low[i]) * 0.4) and (
                                self.df.amount[i] > (self.df.amount[i]+self.df.amount[i+1]+self.df.amount[i+2]+self.df.amount[i+3]+self.df.amount[i+4]) / 5):
                        long_up_shadow.append(i)

            # 筛选
            data = self.angle_data()
            angle, a, b, reg = self.line_model(data)
        else:
            angle = 0
        if len(self.df) > 60:
            # 振幅限制计算
            drop3 = 0
            drop4 = 0
            drop5 = 0
            yin = 0
            yang = 0
            for i in range(50):
                if self.df.open[i] - self.df.close[i] >= 0:
                    yin += 1
                else:
                    yang += 1

                if 0.03 <= (self.df.close[i + 1] - self.df.close[i]) / self.df.close[i + 1] < 0.04:
                    drop3 += 1
                elif 0.04 <= (self.df.close[i + 1] - self.df.close[i]) / self.df.close[i + 1] < 0.05:
                    drop4 += 1
                elif 0.05 <= (self.df.close[i + 1] - self.df.close[i]) / self.df.close[i + 1]:
                    drop5 += 1

            e_support, reason_s = self.support_dot()
            df_p, cv_p, price_p, stop_dot_p = self.pressure_line()
            # 从数据库取包含停牌数据（0）的数据
            if (0 < angle < 40) and (reason_s == 'has support') and (cv_p != -1) and (df_p.empty is False) and \
                    (0 <= len(long_up_shadow) < 4) and (len(list(data0.close[:60].loc[data0.close == 0])) <= 20) and\
                    (min(self.df.low[:5]) >= min(self.df.low[5:80])) and (yang >= yin):
                    # 设以上条件为默认条件，根据语言处理调整选择股策略
                    # 选股趋紧度加一挡
                    # (min(self.df.low[:5]) > 0.98 * e_support)
                    # 选股趋紧度加二档
                    # (min(self.df.low[:10]) > 0.98 * e_support)
                    # 以下为失败策略
                    # 加上振幅drop限制，效果不好
                    # 1 and (drop3 <= 3) and (drop4 <= 2) and (drop5 == 0) and (drop3 + drop4 <= 3):
                self.stock_box.append(self.stock_id)

        return self.stock_box

    def stocks_choose_for_sale(self):
        """
        # 用60天数据改变了角度计算的原50天数据，改变k线在60日均线上方被判不及格的现象
        :return: 
        """
        data0 = data_process.Get_DataFrame_0(self.stock_id, self.date)
        # long_up_shadow长上影线序列列表
        long_up_shadow = []
        if len(list(data0.close[:150].loc[data0.close == 0])) <= 30:
            for i in range(60):
                if self.df.close[i] > self.ave_price_60[i]:
                    if ((self.df.high[i] - max(self.df.close[i], self.df.open[i])) >= (
                                self.df.high[i] - self.df.low[i]) * 0.5) and (
                                self.df.amount[i] > (self.df.amount[i]+self.df.amount[i+1]+self.df.amount[i+2]+self.df.amount[i+3]+self.df.amount[i+4]) / 5):
                        long_up_shadow.append(i)

                        # 筛选
            data = self.angle_data(stop_dot=60)
            angle, a, b, reg = self.line_model(data)
        else:
            angle = 0
        if len(self.df) > 60:
            # # 振幅限制计算
            # drop3 = 0
            # drop4 = 0
            # drop5 = 0
            # for i in range(60):
            #     if 0.03 <= (self.df.close[i + 1] - self.df.close[i]) / self.df.close[i + 1] < 0.04:
            #         drop3 += 1
            #     elif 0.04 <= (self.df.close[i + 1] - self.df.close[i]) / self.df.close[i + 1] < 0.05:
            #         drop4 += 1
            #     elif 0.05 <= (self.df.close[i + 1] - self.df.close[i]) / self.df.close[i + 1]:
            #         drop5 += 1
            #
            # e_support, reason_s = self.support_dot()
            df_s, cv_s, price_s, stop_dot_s = self.support_line()
            if (cv_s == 0) and (self.ave_price_60[0] <= price_s):
                cv_s = 1

            df_p, cv_p, price_p, stop_dot_p = self.pressure_line()
            print 'a'
            # 从数据库取包含停牌数据（0）的数据
            if (0 < angle < 40) and (cv_s == 1) and (cv_p != -1) and (df_p.empty is False) and \
                    (0 <= len(long_up_shadow) < 4) and (len(list(data0.close[:60].loc[data0.close == 0])) <= 20) and \
                    (self.df.low[0] >= min(self.df.low[1:100])):
                # and (min(self.df.low[:5]) > 0.98 * e_support):
                # stock_box 程序2去掉的是1、2，stock_box 程序1去掉的是1，stock_box 程序3如上
                # 2 and (min(self.df.low[:10]) < 0.98 * e_support):
                # 加上振幅drop限制，效果不好
                # 1 and (drop3 <= 3) and (drop4 <= 2) and (drop5 == 0) and (drop3 + drop4 <= 3):
                self.stock_box.append(self.stock_id)
        return self.stock_box


if __name__ == "__main__":
    import datetime
    start = datetime.datetime.now()
    stock_box = []
    stock = '002716'
    obj = Calculation(stock, stock_box)
    obj.stocks_choose()
    print 'stock', type(stock)
    print 'stock_box', stock_box

    # stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
    #                                dtype={'code': np.str})
    # code = stock_basic_list.code
    # for stock in list(code):
    #     obj = Calculation(stock, stock_box)
    #     obj.stocks_choose()
    #     print 'stock', stock
    #     print 'stock_box', stock_box
    #     print '*' * 30

    end = datetime.datetime.now()
    secondsdiff = (end - start).seconds
    minutesdiff = round(secondsdiff / 60, 1)
    print 'stock_select_minutes', minutesdiff