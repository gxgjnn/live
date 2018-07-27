# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import pandas as pd
import time
from sqlalchemy import create_engine
import os
import ConfigParser
from utils import data_process


class Account:
    """
    # 账户信息
    """

    def __init__(self):
        # 连接以为存储
        self.conf_dir = os.path.split(os.path.realpath(__file__))[0].replace('SIMULATION', 'conf')
        config = ConfigParser.ConfigParser()
        file_path = os.path.join(self.conf_dir, 'default.ini')
        config.read(file_path)
        db = 'db_back'
        self.db = db
        self.engine = create_engine("mysql+pymysql://" + config.get(db, 'user') + ":" + config.get(db, 'password') + "@"
                                    + config.get(db, 'host') + "/" + config.get(db, 'database') + "?charset=utf8")
        tik = time.strftime("%Y-%m-%d", time.localtime())
        # data = ''
        # stocks_chosen_daily = pd.DataFrame([[tik, data]], columns=['date', 'bad_package'])
        # stocks_chosen_daily.to_sql(con=self.engine, name="bad_package", if_exists='replace', index=False)
        # 20170105, 300139, 晓程科技, buy, 13.63, 200, 2726, 2762, 0, 200, 200, 36, 0
        # 20170105, 300106, 西部牧业, buy, 16.29, 1500, 24432, 24825, 1200, 1500, 1500, 393, 0
        # 20170105, 000150, 宜华健康, buy, 30.29, 600, 18176, 18018, 400, 600, 600, -158, 0
        # 20170105, 002313, 日海通讯, buy, 23.44, 200, 4688, 4580, 0, 200, 200, -108, 0
        # 20170105, 300209, 天泽信息, buy, 24.07, 200, 4814, 4794, 0, 200, 200, -20, 0
        # holding_stock_detail = pd.DataFrame([[ 20170105, 000150, '宜华健康', 'buy', 30.29, 600, 18176, 18018, 400, 600, 600, -158, 0]],
        #                                     columns=['交易日', '证券代码', '证券名称', '持仓方向', '持仓成本价',
        # '总持仓股数', '持仓成本金额', '当前总持仓金额', '昨日持仓', '今日持仓', '可用持仓', '持仓盈亏', '交易盈亏'])
        # holding_stock_detail.to_sql(con=self.engine, name="holding_stock_detail_current", if_exists='append',
        # index=False)
        # order_stock_detail = pd.DataFrame([[tik, 1, '000988', '鼎汉技术', 'sell', 20, 1000,
        #                                     20000, 0, 0, tik, 'undeal']],
        #                                   columns=['交易日', '任务编号', '证券代码', '证券名称', '委托行为',
        # '委托价格', '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
        # order_stock_detail.to_sql(con=self.engine, name="order_stock_detail_current", if_exists='replace',
        #                            index=False)
        # account = pd.DataFrame([[tik, 1000000, 1000000, 0]], columns=['日期','总资产','可用金额','持股金额'])
        # account.to_sql(con=self.engine, name="account", if_exists='append', index=False)
        # account_a = pd.DataFrame([[tik, str(['002716', '300346'])]], columns=['date', 'stocks_chosen_daily'])
        # account_a.to_sql(con=self.engine, name="stocks_chosen_daily", if_exists='append', index=False)
        # time_profit_detail = pd.DataFrame([[tik, 0, 0, 0, 0, 0]], columns=['日期', '当日持仓金额', '昨日持仓盈亏',
        #                                                         '今日持仓盈亏', '近5日盈亏', '近20日盈亏'])
        # time_profit_detail.to_sql(con=self.engine, name="account_profit_detail", if_exists='replace', index=False)
        # total_profit = pd.DataFrame([['600210', '紫江企业', '20170118', 'unknown', 'unknown', '5.29', 'unknown',
        #                               '5.34', '0', 'undeal','unknown']], columns=['证券代码', '证券名称', '首次买入时间',
        #  '清仓时间', '持仓时间','首次买入价', '清仓价', '当前价', '总盈亏', '状态', '清仓理由'])
        # total_profit.to_sql(con=self.engine, name="account_total_profit_detail", if_exists='append', index=False)
        # # 每日取最新取初始金额数
        initial_capital = data_process.get_initial_capital_back()
        self.initial_capital = initial_capital

    def account_detail(self, order_id, holding_stock_detail, order_stock_detail, date):
        """

        :param order_id: 为了不要重复计算影响money_available的值
        :param holding_stock_detail: 当日持仓表
        :param order_stock_detail: 当日下单表
        :return: 
        """
        # 每批次委托都要刷新该函数，每次收盘（3：05pm）再刷新一次，一共三次
        # 账户总资产， 当前可用金额， 持仓总金额------存
        current_holding = 0
        if holding_stock_detail.empty is False:
            current_holding = holding_stock_detail.iloc[:, 7].sum()
        money_available = self.initial_capital
        account = data_process.get_account_back()
        total_capital = account.iloc[-1, 1]
        if order_id != 0:
            # 每次刷新后的可用资金
            lock_amount = 0
            for i in range(len(order_stock_detail)):
                if (order_stock_detail.iloc[i, 1] == order_id) and (order_stock_detail.iloc[i, 4] == 'buy'):
                    order_amount = order_stock_detail.iloc[i, 7]
                    lock_amount += order_amount
            money_available = int(money_available - lock_amount)
            # 总资产保持不变
        else:
            lock_amount_undeal = 0
            for i in range(len(order_stock_detail)):
                if (order_stock_detail.iloc[i, 11] == 'undeal') and (order_stock_detail.iloc[i, 4] == 'buy'):
                    order_amount_undeal = order_stock_detail.iloc[i, 7]
                    lock_amount_undeal += order_amount_undeal

            for i in range(len(order_stock_detail)):
                if (order_stock_detail.iloc[i, 11] == 'deal') and (order_stock_detail.iloc[i, 4] == 'sell'):
                    order_amount_deal = order_stock_detail.iloc[i, 7]
                    lock_amount_undeal += order_amount_deal
            money_available = int(money_available + lock_amount_undeal)
            # 总资产会变
            total_capital = money_available + current_holding

        # 每次刷新后存进表Account
        # tik = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        tik = date
        df = pd.DataFrame([[tik, total_capital, money_available, current_holding]], columns=['日期', '总资产',
                                                                                             '可用金额', '持股金额'])
        df.to_sql(con=self.engine, name="account", if_exists='append', index=False)

        return total_capital, money_available, current_holding

    def time_profit(self, date, current_amount, holding_profit_yesterday, nowadays_profit,
                    week_profit, month_profit):
        time_profit_detail = pd.DataFrame([[date, current_amount, holding_profit_yesterday,
                                            nowadays_profit, week_profit, month_profit]],
                                          columns=['日期', '当日持仓金额', '昨日持仓盈亏', '今日持仓盈亏', '近5日盈亏', '近20日盈亏'])

        time_profit_detail.to_sql(con=self.engine, name="account_profit_detail", if_exists='append', index=False)

        return time_profit_detail

    def total_profit(self, stock_id, stock_name, first_buy_time, last_sell_time, holding_period, origin_price,
                     last_price, current_price, deal_profit, status, refused_reason):
        # 每个股票清仓后存入，账户盈利情况
        total_profit_detail = pd.DataFrame([[stock_id, stock_name, first_buy_time, last_sell_time, holding_period,
                                             origin_price, last_price, current_price, deal_profit, status, refused_reason]],
                                           columns=['证券代码', '证券名称', '首次买入时间', '清仓时间', '持仓时间', '首次买入价', '清仓价', '当前价',
                                                    '总盈亏', '状态', '清仓理由'])
        # 读取数据
        total_profit = data_process.get_total_profit_back()
        total_profit_0 = total_profit
        # 是否重复数据
        for i in range(len(total_profit)):
            if (stock_id == total_profit.iloc[i, 0]) and (total_profit.iloc[i, -2] == 'undeal'):
                total_profit_0 = total_profit.drop(total_profit.index[i])
        # 数据添加
        total_profit = pd.concat([total_profit_0, total_profit_detail])
        # 数据替换
        total_profit.to_sql(con=self.engine, name="account_total_profit_detail", if_exists='replace', index=False)

        return total_profit_detail


class Current(Account):
    def current_holding_detail(self, date, stock_id, stock_name, hold_status, origin_price, total_num, origin_amount,
                               current_amount, yesterday_num, nowadays_num, available_num, holding_profit, deal_profit):
        # 当日持仓详情
        holding_stock_detail = pd.DataFrame([[date, stock_id, stock_name, hold_status, origin_price, total_num,
                                              origin_amount, current_amount, yesterday_num, nowadays_num, available_num,
                                              holding_profit, deal_profit]],
                                            columns=['交易日', '证券代码', '证券名称', '持仓方向', '持仓成本价', '总持仓股数', '持仓成本金额',
                                                     '当前总持仓金额', '昨日持仓', '今日持仓', '可用持仓', '持仓盈亏', '交易盈亏'])
        # 获取数据表
        current_holding_detail = data_process.get_holding_stock_detail_current_back()
        # 是否重复数据
        current_holding_detail_0 = current_holding_detail
        for i in range(len(current_holding_detail)):
            if stock_id == current_holding_detail.iloc[i, 1]:
                current_holding_detail_0 = current_holding_detail.drop(current_holding_detail.index[i])
        # 数据添加
        current_holding_detail = pd.concat([current_holding_detail_0, holding_stock_detail])
        # 数据替换
        current_holding_detail.to_sql(con=self.engine, name="holding_stock_detail_current", if_exists='replace',
                                      index=False)

        return holding_stock_detail

    def current_place_order(self, date, order_id, stock_id, stock_name, order_status, order_price, order_num,
                            lock_amount, deal_amount, deal_num, order_time, deal_status):
        # 当日委托详情
        order_stock_detail = pd.DataFrame([[date, order_id, stock_id, stock_name, order_status, order_price, order_num,
                                            lock_amount, deal_amount, deal_num, order_time, deal_status]],
                                          columns=['交易日', '任务编号', '证券代码', '证券名称', '委托行为', '委托价格',
                                                   '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
        # 获取数据表
        current_place_order = data_process.get_order_stock_detail_current_back()
        current_place_order_0 = current_place_order
        # # 是否重复数据
        for i in range(len(current_place_order)):
            if (stock_id == current_place_order.iloc[i, 2]) and (order_price == current_place_order.iloc[i, 5]) and (
                        current_place_order.iloc[i, -1] == 'undeal'):
                current_place_order_0 = current_place_order.drop(current_place_order.index[i])
        # 数据添加
        current_place_order1 = pd.concat([current_place_order_0, order_stock_detail])
        # 数据替换
        current_place_order1.to_sql(con=self.engine, name="order_stock_detail_current", if_exists='replace',
                                   index=False)

        return order_stock_detail

    def current_deal_detail(self, date, order_id, stock_id, stock_name, status, deal_price, deal_num, deal_time):
        # 当日成交详情
        deal_stock_detail = pd.DataFrame([[date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                           deal_time]],
                                         columns=['交易日', '任务编号', '证券代码', '证券名称', '交易行为', '成交价格',
                                                  '成交数量', '成交时间'])
        deal_stock_detail.to_sql(con=self.engine, name="deal_stock_detail_current", if_exists='append', index=False)

        return deal_stock_detail


class History(Current):
    """
    # 其实就是存储函数
    """

    def holding_detail(self, date, stock_id, stock_name, hold_status, origin_price, total_num, origin_amount,
                       current_amount, yesterday_num, nowadays_num, available_num, holding_profit, deal_profit):
        # 历史持仓详情
        holding_stock_detail = pd.DataFrame([[date, stock_id, stock_name, hold_status, origin_price, total_num,
                                              origin_amount, current_amount, yesterday_num, nowadays_num, available_num,
                                              holding_profit, deal_profit]],
                                            columns=['交易日', '证券代码', '证券名称', '持仓方向', '持仓成本价', '总持仓股数', '持仓成本金额',
                                                     '当前总持仓金额', '昨日持仓', '今日持仓', '可用持仓', '持仓盈亏', '交易盈亏'])

        holding_stock_detail.to_sql(con=self.engine, name="holding_stock_detail_history", if_exists='append',
                                    index=False)

        return holding_stock_detail

    def place_order(self, date, order_id, stock_id, stock_name, order_status, order_price, order_num, lock_amount,
                    deal_amount, deal_num, order_time, deal_status):
        # 历史委托详情
        order_stock_detail = pd.DataFrame([[date, order_id, stock_id, stock_name, order_status, order_price, order_num,
                                            lock_amount, deal_amount, deal_num, order_time, deal_status]],
                                          columns=['交易日', '任务编号', '证券代码', '证券名称', '委托行为', '委托价格',
                                                   '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
        # 存储
        order_stock_detail.to_sql(con=self.engine, name="order_stock_detail_history", if_exists='append', index=False)

        return order_stock_detail

    def deal_detail(self, date, order_id, stock_id, stock_name, status, deal_price, deal_num, deal_time):
        # 历史成交详情
        deal_stock_detail = pd.DataFrame([[date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                           deal_time]],
                                         columns=['交易日', '任务编号', '证券代码', '证券名称', '交易行为', '成交价格',
                                                  '成交数量', '成交时间'])
        deal_stock_detail.to_sql(con=self.engine, name="deal_stock_detail_history", if_exists='append', index=False)

        return deal_stock_detail


if __name__ == '__main__':
    # holding_stock_detail = data_process.get_holding_stock_detail_current()
    # order_stock_detail = data_process.get_order_stock_detail_current()
    # order_id = 0

    obj0 = Account()
    obj1 = Current()
    obj2 = History()

    # tik = time.strftime("%Y-%m-%d", time.localtime())
    # time_profit_detail = pd.DataFrame([[tik,1000000,1000000,0]],
    #                                   columns=['日期', '总资产', '可用金额', '持股金额'])
    # time_profit_detail.to_sql(con=self.engine, name="account_profit_detail", if_exists='append', index=False)

    # order_ = 1
    # holding_stock_detail_ = pd.DataFrame([])
    # order_stock_detail_ = data_process.get_order_stock_detail_current_back()
    # obj0.account_detail(order_, holding_stock_detail_, order_stock_detail_)

    # obj.account_detail(order_id, holding_stock_detail, order_stock_detail)

    # obj1.current_holding_detail(20170105, '002313', '日海通讯', 'buy', 23.44, 200, 4688, 4580, 0, 200, 200, -108, 0)
    # '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0'
    # '002022', '科华生物', '20170103', '20170105', '2', '20.19', '20.28', '20.2', '19.09', 'deal', '角度超出阈值'
    # '002265', '西仪股份', '20170103', '20170105', '2', '19.27', '21.96', '22.78', '532.29', 'deal', '清仓价清仓'
    # '300207', '欣旺达', '20170109', 'unknown', 'unknown', '12.24', 'unknown', '12.24', '0', 'undeal', 'unknown'
    # '601991', '大唐发电', '20170103', '20170110', '7', '3.84', '3.88', '3.88', '27', 'deal', '收盘价近似最低价'
    # '603598', '引力传媒', '20170106', '20170110', '4', '21.68', '21.88', '21.09', '51.47', 'deal', '收盘价近似最低价'
    # '600965', '福成股份', '20170109', '20170110', '1', '13.68', '13.7', '13.71', '0.66', 'deal', '收盘价近似最低价'
    # '000035', '中国天楹', '20170110', 'unknown', 'unknown', '7.42', 'unknown', '7.44', '0', 'undeal', 'unknown'
    # '002138', '顺络电子', '20170110', 'unknown', 'unknown', '17.19', 'unknown', '17.11', '0', 'undeal', 'unknown'
    # '600112', '*ST天成', '20170110', 'unknown', 'unknown', '10.72', 'unknown', '10.67', '0', 'undeal', 'unknown'
    # '600590', '泰豪科技', '20170103', '20170111', '8', '18.02', '16.02', '16.77', '-756.5', 'deal', 'unknown'
    # '600175', '美都能源', '20170109', '20170111', '2', '5.08', '5.02', '5.12', '-172.97', 'deal', 'unknown'
    # '601901', '方正证券', '20170110', '20170111', '1', '7.53', '7.48', '7.49', '-41.81', 'deal', 'unknown'

    # obj0.total_profit('600112', '*ST天成', '20170110', 'unknown', 'unknown', '10.72', 'unknown', '10.67', '0', 'undeal', 'unknown')