# -*- coding: utf-8 -*-

import pandas as pd
from utils import data_process
from STOCK_CHOOSE.stock_box import Calculation
from DEAL.strategy import Strategy
import numpy as np
from DEAL.strategy2 import Strategy2
from DEAL import strategy2a
import time
# 选股
stock_box = []
stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                               dtype={'code': np.str})
code = stock_basic_list.code
for stock in list(code):
    obj = Calculation(stock)
    obj.stocks_choose()
    print 'stock', stock
    print 'stock_box', stock_box
    print '*' * 30

# 如果选出的股票包含持仓的股票，那么要删除
running_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/running_box.csv')
research_box = pd.read_csv()
for stock_id in stock_box:
    if (stock_id in list(running_box.loc[:, 'stock_id'])) or (stock_id in list(research_box.loc[:, 'stock_id'])):
        stock_box.remove(stock_id)

# 合并选股股票和前几日选股未买入股票,删除已持仓的待买入的股票
waiting_box = pd.read_csv('C:/Users/liquan/PycharmProjects/live/DEAL/waiting_box.csv')
if stock_id in list(running_box.loc[:, 'stock_id']):
    waiting_box = waiting_box.loc[waiting_box.stock_id != stock_id, ]
    waiting_box.to_csv('waiting_box.csv', encoding='utf-8', index_label=False, mode='w')
stock_box = list(set(stock_box.extend(list(waiting_box.loc[:, 'stock_id']))))


# 买股
obj1 = Strategy(stock)
for stock in stock_box:
    price_buy, price_sell, cash, num = obj1.buying()
    # 交易
    print
    # 然后接模拟实盘，或deal.py

# 卖股
for stock in running_box.stock_id:
    price_buy, price_sell, cash, num = obj1.selling()
    # 交易
    print
    # 然后接模拟实盘，或deal.py
    # obj = Deal(num=num, stock_id=stock_id, price_sell=price_sell, price_buy=price_buy)
    # deal_datail, running_box = obj.store()



