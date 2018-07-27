# -*- coding: utf-8 -*-

#from __future__ import unicode_literals
from jaqs.trade.tradeapi import TradeApi
import math
import tushare as ts
from utils import data_process
import numpy as np
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def trade_simulation_connection():
    """
    # 连接线上交易系统
    :return: 
    """
    # 登录仿真系统地址
    tapi = TradeApi(addr="tcp://gw.quantos.org:8901")
    user_info, msg = tapi.login("13661860320", "eyJhbGciOiJIUzI1NiJ9.eyJjcmVhdGVfdGltZSI6IjE1MTYwMTAzNjg3MTUiLCJpc3MiOiJhdXRoMCIsImlkIjoiMTM2NjE4NjAzMjAifQ.8sajz3mLHJM1JQEreIwk6BnWNIb5oCIHVDmlhHgmGwE")
    print user_info
    print msg
    # 只用一次绑定策略号
    # sid, msg = tapi.use_strategy(7441)
    return tapi


def trade_data(stock_id):
    """
    # 获取线上交易数据
    :return: 持仓股数num_sell---   # 读取存储位置的持仓详情，如果存在可卖金额为实数，如果不存在则为0
              可用资金money_available
    """
    # 查询账户信息
    # 返回当前的策略帐号的账户资金信息。
    df0 = data_process.get_holding_stock_detail_current()
    for i in range(len(df0.iloc[:, 1])):
        df0.iloc[i, 1] = str(df0.iloc[i, 1]).zfill(6)

    num_sell = 0
    for i in range(len(df0)):
        if stock_id == df0.iloc[i, 1]:
            num_sell = df0.iloc[i, 5]

    df1 = data_process.get_account()
    money_available = df1.iloc[-1, 2]
    return num_sell, money_available


def trade_data_back(stock_id):
    """
    # 获取线上交易数据
    :return: 持仓股数num_sell---   # 读取存储位置的持仓详情，如果存在可卖金额为实数，如果不存在则为0
              可用资金money_available
    """
    # 查询账户信息
    # 返回当前的策略帐号的账户资金信息。
    df0 = data_process.get_holding_stock_detail_current_back()
    for i in range(len(df0.iloc[:, 1])):
        df0.iloc[i, 1] = str(df0.iloc[i, 1]).zfill(6)

    num_sell = 0
    for i in range(len(df0)):
        if stock_id == df0.iloc[i, 1]:
            num_sell = df0.iloc[i, 5]

    df1 = data_process.get_account_back()
    money_available = df1.iloc[-1, 2]
    return num_sell, money_available


def num_transfer(money_available, num_sell, price):
    """
    # 每个股票买卖数量的计算函数
    :return: num_buy, 如果已持仓部分，那么要减去以持仓的部分在返回num_buy
    """
    each_cash = 20000.0

    strict_num = each_cash / price
    num_buy0 = math.ceil(strict_num / 100) * 100
    num_buy = num_buy0 - num_sell

    # 从此处为了保证剩余资金
    if money_available <= 30000:
        num_buy = 0
        print 'money alarm'
    return num_buy


if __name__ == '__main__':
    v_s_data = ts.get_realtime_quotes('601699')







    tapi = trade_simulation_connection()
    trade_data()


    # 单标的下单
    task_id, msg = tapi.place_order("000025.SZ", "Buy", 57, 100)
    print "msg:", msg
    print "task_id:", task_id

    # 批量下单
    orders = [
        {"security": "000025.SZ", "action": "Buy", "price": 38, "size": 1000},
        {"security": "000025.SZ", "action": "Buy", "price": 39, "size": 1000},
        {"security": "000025.SZ", "action": "Buy", "price": 40, "size": 1000}
    ]
    task_id, msg = tapi.place_batch_order(orders)
    print task_id
    print msg