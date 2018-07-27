# -*- coding: utf-8 -*-

import time
import pandas as pd


class Deal(object):
    """
    open_tax，买入时印花税 (只股票类标的收取，基金与期货不收)
    close_tax，卖出时印花税 (只股票类标的收取，基金与期货不收)
    open_commission，买入时佣金
    close_commission, 卖出时佣金
    close_today_commission, 平今仓佣金
    min_commission, 最低佣金，不包含印花税
    running_box,持仓情况
    deal_detail,交易明细
    """
    def __init__(self):
        pass
        # self.stock_id = stock_id
    # 股票类每笔交易时的手续费是：买入时佣金万分之三，卖出时佣金万分之三加千分之一印花税, 每笔交易佣金最低扣5块钱

    def order_cost(self, num, price, close_tax, open_commission, close_commission, min_commission):

        commission_buy = open_commission * num * price
        commission_sell = close_commission * num * price + close_tax * num * price

        if commission_buy < 5:
            commission_buy = min_commission
        if commission_sell < 5:
            commission_sell = min_commission

        return commission_buy, commission_sell

    def pocket(self):
        """
        
        :return: 剩余额度
        """
        first_cash = 1000000
        if running_box.empty and deal_detail.empty:
            pocket = first_cash
        else:
            rest = deal_detail.iloc[-1, 5]
            pocket = rest
        return pocket

    def buy(self, num, price):
        """
        此处是人为操作，只存在资金不够买不进的情况
        :param num: 买入的股票数量
        :param price: 买价
        :return: running_box,deal_detail所需的一切
        """
        global running_box
        commission_buy, commission_sell = self.order_cost(num, price, close_tax=0.001, open_commission=0.0003,
                                                          close_commission=0.0003, min_commission=5)
        facility = num * price + commission_buy
        tik_tok = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        pocket = self.pocket()

        # flag = 1 按标准买入,flag = 0部分买入
        if all(pd.Series(self.stock_id).isin(running_box.loc[:, 'stock_id'])):
            raw_num = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0]
            new_num = raw_num + num
            running_box.loc[running_box.stock_id == self.stock_id, 'bought_price'] = price
            running_box = running_box.loc[running_box.bought_num != raw_num, ]
            flag = 0
        else:
            flag = 1

        try:
            if ((pocket - facility) > 0) and (flag == 0):
                rest = pocket - facility
                stock_detail = pd.DataFrame([[self.stock_id, price, new_num, tik_tok]],
                                            columns=['stock_id', 'bought_price', 'bought_num', 'bought_time'],
                                            index=[0])
                running_box = pd.concat([running_box, stock_detail], axis=0)
                profit = list(running_box.loc[running_box.stock_id == self.stock_id, 'profit'])[0]

            elif ((pocket - facility) > 0) and (flag == 1):
                rest = pocket - facility
                stock_detail = pd.DataFrame([[self.stock_id, price, num, tik_tok]],
                                            columns=['stock_id', 'bought_price', 'bought_num', 'bought_time'],
                                            index=[0])
                running_box = pd.concat([running_box, stock_detail], axis=0)
                profit = 0
            else:
                rest = 0
                print 'pocket empty'
        except Exception, e:
            print e

        # status = 1买，0卖
        status = 1
        profit = 0
        return status, tik_tok, self.stock_id, price, num, facility, rest, flag, profit, running_box

    def sell(self, num, price, cash):
        """
        此处是人为操作，不存在卖不出去的情况,策略中暂时不存在卖部分的情况
        :param num: 卖出股票的数量
        :param price:卖价 
        :param cash: 已经计算好的卖出金额（facility）
        :return: running_box,deal_detail所需的一切
        """
        global running_box
        commission_buy, commission_sell = self.order_cost(num, price, close_tax=0.001, open_commission=0.0003,
                                                          close_commission=0.0003, min_commission=5)
        facility = cash
        tik_tok = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        pocket = self.pocket()
        # 卖出所得金额
        rest = pocket + facility
        # status = 1买，0卖
        status = 0
        # 删除卖空后的股票 flag = 1 个股卖空标记，0 个股部分卖出标记
        running_box = running_box.loc[running_box.stock_id != self.stock_id, ]
        bought_num = list(running_box.loc[running_box.stock_id == self.stock_id, 'num'])[0]
        bought_price = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_price'])[0]
        # flag = 1 按标准买入,flag = 0部分买入
        if num != bought_num:
            flag = 0
            left_num = list(running_box.loc[running_box.stock_id == self.stock_id, 'bought_num'])[0] - num
            profit_0 = list(deal_detail.loc[deal_datail.stock_id == self.stock_id, 'profit'])[-1]
            profit_1 = (price - bought_price) * num - commission_sell
            profit = profit_0 + profit_1
            stock_detail = pd.DataFrame([[self.stock_id, price, left_num, tik_tok]],
                                        columns=['stock_id', 'bought_price', 'bought_num', 'bought_time'],
                                        index=[0])
            running_box = pd.concat([running_box, stock_detail], axis=0)
        else:
            flag = 1
            profit = (price - bought_price) * num
        return status, tik_tok, self.stock_id, price, num, facility, rest, flag, profit, running_box

    def store(self, number, price_buy, price_sell, cash):
        global deal_detail
        if (price_buy != 0) and (price_sell == 0):
            status, tik_tok, self.stock_id, price, num, facility, rest, flag, profit, \
            running_box = self.buy(number, price_buy)
            bought_detail = pd.DataFrame([[status, tik_tok, self.stock_id, price, num, rest, flag, profit, explain]],
                                         columns=['status', 'tik_tok', 'stock_id', 'price', 'num', 'rest',
                                                  'flag', 'profit', 'explain'], index=[0])
            deal_detail = pd.concat([deal_detail, bought_detail], axis=0)
        if (price_buy == 0) and (price_sell != 0):
            status, tik_tok, stock_id, price, num, facility, rest, flag, profit, running_box = \
                self.sell(number, price_sell, cash)
            sold_detail = pd.DataFrame([[status, tik_tok, stock_id, price, num, rest, flag, profit, explain]],
                                       columns=['status', 'tik_tok', 'stock_id', 'price', 'num', 'rest',
                                                'flag', 'profit', 'explain'], index=[0])
            deal_detail = pd.concat([deal_detail, sold_detail], axis=0)
        running_box.to_csv('running_box.csv', encoding='utf-8', index_label=False, mode='w')
        deal_detail.to_csv('deal_detail.csv', encoding='utf-8', index_label=False, mode='w')
        return deal_detail, running_box


if __name__ == "__main__":
    """
    更改后未测试
    """
    # running_box = pd.DataFrame([])  #用于记录持仓股票，这行代码只能用一次，第一次
    # deal_detail = pd.DataFrame([])
    explain = 'test'
    running_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/running_box.csv')
    deal_detail = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/deal_detail.csv')
    stock = '600017.XSHG'
    num1 = 500
    price_sell=4.32
    df_close = pd.read_csv('C:/Users/liquan/Desktop/krama/df_close.csv')
    #price_buy = list(df_close.loc[136:, stock_id])[-1]
    price_buy = 0
    obj = Deal(num=num1,stock_id = stock,price_sell =price_sell,price_buy = price_buy)
    deal_datail,running_box = obj.store()
    print 'deal_detail\n',deal_datail
    print 'running_box\n',running_box
    # deal_datail,running_box = obj.store()
    # print 'deal_detail\n',deal_datail
    # print 'running_box\n',running_box


    # stock_id = '600017.XSHG'
    # num = 1000
    # price_sell= list(df_close.loc[136:, stock_id])[-2]
    # price_buy = 0
    # obj = DEAL(num=num,stock_id = stock_id,price_sell =price_sell,price_buy = price_buy)
    # deal_datail,running_box = obj.store()
    # print 'deal_detail\n',deal_datail
    # print 'running_box\n',running_box


# running_box里已经有的不买，why，可以重复买
#存储