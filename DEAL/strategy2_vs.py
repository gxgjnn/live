# -*- coding: utf-8 -*-

import tushare as ts
from strategy2_initial import *
from utils import create_data
from DEAL.info_online import *


class VS(Wave):
    """
    # df = [0,1,2,3,4,5,6,7,8,9],可变系数
    # stock_box和running_box实时买入，running_box实时卖出
    # 通过running_box/模拟持仓系统，需要得到剩余可用资金、持仓股票数据等
    """
    def __init__(self, stock_id, obj_5):
        super(Wave, self).__init__(stock_id)
        self.obj_5 = obj_5
        df_s, cv_s, price_s, stop_dot_s = self.support_line()
        df_p, cv_p, price_p, stop_dot_p = self.pressure_line()
        self.df_s = df_s
        self.cv_s = cv_s
        self.price_s = price_s
        self.stop_dot_s = stop_dot_s
        self.df_p = df_p
        self.cv_p = cv_p
        self.price_p = price_p
        self.stop_dot_p = stop_dot_p

    def buy_real_time(self, data):
        """
        # 跳空回落买入1/10
        :param data: 实时数据
        :return: DataFrame({'price':,'num':})
        """
        data_buy_ = pd.DataFrame([])
        if data.high[0] < self.price_p:
            if data.low[0] > self.ave_price_5[0]:
                price = self.ave_price_5[0]
                df = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                num = self.obj_5.num_buy_process(coe=1, data=df)
                data_buy_ = pd.DataFrame({'price': price, 'num': num})
        return data_buy_

    def sell_real_time(self, data):
        """
        # 各种情况。。。。。卖出要排序
        # 计算延时时间，如果可以获取当前卖二价，则挂单卖，如果有挂最新卖价按钮，再好不过
        :return: DataFrame({'price':,'num':})。。。。
        """
        data_sell0 = pd.DataFrame([])
        # 涨停止盈,9%以上卖出什么的10%
        if float(data.price[0]) >= self.df.close[0] * 1.09:
            price = float(data.a3_p[0])
            df = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            num = self.obj_5.num_buy_process(coe=1, data=df)
            data_sell0 = pd.DataFrame({'price': price, 'num': num}, index=[0])

        # 长上影线止盈,卖3价，1/10
        data_sell1 = pd.DataFrame([])
        close_ave5 = create_data.ave_data_create(self.df.close, 5)
        open_ave5 = create_data.ave_data_create(self.df.open, 5)
        high_ave5 = create_data.ave_data_create(self.df.high, 5)
        low_ave5 = create_data.ave_data_create(self.df.low, 5)
        if ((float(data.high[0]) - max(float(data.open[0]), float(data.price[0]))) / (float(data.high[0]) - float(data.low[0])) >= 0.5) or \
                ((high_ave5[0] - max(open_ave5[0], close_ave5[0])) / (high_ave5[0] - low_ave5[0]) >= 0.5):
            if float(data.volume[0]) > self.df.volume[0:5].mean():
                price = float(data.a3_p[0])
                df = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
                num = self.obj_5.num_buy_process(coe=1, data=df)
                data_sell1 = pd.DataFrame({'price': price, 'num': num}, index=[0])

        # 跳空止盈,卖3价，1/10
        data_sell2 = pd.DataFrame([])
        if float(data.low[0]) > self.ave_price_5[0]:
            price = float(data.a3_p[0])
            df = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
            num = self.obj_5.num_buy_process(coe=1, data=df)
            data_sell2 = pd.DataFrame({'price': price, 'num': num}, index=[0])

        data_sell_ = pd.concat([data_sell0, data_sell1, data_sell2])
        # 因为目前买价和买量都是一样的，所以不需要分类
        # 可能会有一个小bug，当一次性全部卖完的时候，也就是说，当vs的情况发生一个事件以上的时候，存量比卖出的数量要少。。。。
        if data_sell_.empty is False:
            num = data_sell_.num.sum()
            price = data_sell_.price.drop_duplicates()[0]
            data_sell_ = pd.DataFrame({'price': price, 'num': num}, index=[0])

        return data_sell_

if __name__ == '__main__':
    # 买
    # stock = '601699'
    # vs_data = ts.get_realtime_quotes(stock)
    # obj1 = VS(stock)
    # vs_data = ts.get_realtime_quotes(stock)
    # data_buy = obj1.buy_real_time(vs_data)
    # print 'data_buy', data_buy
    # 卖
    stock = '601699'
    price = float(ts.get_realtime_quotes(stock).price[0])
    num_sell, available_money = trade_data(stock)
    num_buy = num_transfer(available_money, num_sell, price)
    obj_5 = Initial(stock, num_buy=num_buy, num_sell=num_sell)
    obj1 = VS(stock, obj_5)
    vs_data = ts.get_realtime_quotes(stock)
    data_sell = obj1.sell_real_time(vs_data)
    print 'data_sell', data_sell
