# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import pandas as pd
from db_connection import Connection
import sys
sys.path.append("..")


def Get_DataFrame_0(stock_id, date):
    """

    :param stock_id: 
    :return: history_data from 2017-01-01 till now with 0
    """

    conn = Connection().conn_destination()
    try:
        sql = ('SELECT date,max(case code when ' + str(stock_id) + ' then open else 0 end) open,'
                                                                   'max(case code when ' + str(
            stock_id) + ' then close else 0 end) close,'
                        'max(case code when ' + str(stock_id) + ' then high else 0 end) high,'
                                                                'max(case code when ' + str(
            stock_id) + ' then low else 0 end) low,'
                        'max(case code when ' + str(stock_id) + ' then volume else 0 end) volume,'
                                                                'max(case code when ' + str(
            stock_id) + ' then amount else 0 end) amount FROM stock.fq_day_qfq  '
                        'where date <= CONCAT(' + str(date) + ', "")'
                        'group by date desc ')
        history_data = pd.read_sql(sql, conn)
        return history_data
    except Exception, e:
        print 'get history DataFrame wrong by',
        print e
    conn.close()


def Get_DataFrame(stock_id, date):
    """

    :param stock_id: 
    :return: history_data from 2017-01-01 till now without 0
    """

    conn = Connection().conn_destination()
    try:
        sql = ('SELECT *  FROM stock.fq_day_qfq WHERE code = ' + str(stock_id) + ' AND date <= CONCAT('+date+', "") order by date desc')
        history_data = pd.read_sql(sql, conn)
        return history_data
    except Exception, e:
        print 'get history DataFrame wrong by',
        print e
    conn.close()


def get_latest(stock_id):
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ('SELECT date,open,close,high,low,volume,amount FROM stock.fq_day_chuquan where date = '
               'curdate() and code =  ' + str(stock_id) + '')
        history_data = pd.read_sql(sql, conn)
        return history_data
    except Exception, e:
        print 'get_latest wrong by', stock_id
        print e
    conn.close()


def get_order_stock_detail_history(stock_id, date):
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ('SELECT * FROM stock.order_stock_detail_history where `证券代码` = ' + str(stock_id) + ' and `交易日` = CONCAT('+date+', "")')
        deal_history = pd.read_sql(sql, conn)
        return deal_history
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_initial_capital():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT `可用金额` FROM stock.account")
        latest_data = pd.read_sql(sql, conn)
        capital = latest_data.iloc[-1, 0]
        return capital
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_holding_stock_detail_current():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("select * from stock.holding_stock_detail_current")
        holding_stock_detail_current = pd.read_sql(sql, conn)
        return holding_stock_detail_current
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_holding_without_0():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("select * from stock.holding_stock_detail_current where `总持仓股数` <> 0")
        holding_stock_detail_current = pd.read_sql(sql, conn)
        return holding_stock_detail_current
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_order_stock_detail_current():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.order_stock_detail_current")
        order_stock_detail_current = pd.read_sql(sql, conn)
        return order_stock_detail_current
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_order_stock_latest():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.order_stock_latest")
        order_stock_latest = pd.read_sql(sql, conn)
        return order_stock_latest
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_account():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.account")
        account = pd.read_sql(sql, conn)
        return account
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_account_profit():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.account_profit_detail")
        account_profit = pd.read_sql(sql, conn)
        return account_profit
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_box():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.stocks_chosen_daily")
        box = pd.read_sql(sql, conn)
        return box
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_package():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.holding_bad_package_daily")
        package = pd.read_sql(sql, conn)
        return package
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_total_profit():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_destination()
    try:
        sql = ("SELECT * FROM stock.account_total_profit_detail")
        total_profit = pd.read_sql(sql, conn)
        return total_profit
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_current_order():
    """
    # 删除当日委托表
    """
    conn = Connection().conn_destination()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM stock.order_stock_detail_current")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_current_deal():
    """
    # 删除当日成交表
    """
    conn = Connection().conn_destination()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM stock.deal_stock_detail_current")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_current_hold_0():
    """
    # 删除持仓表中卖空的股票
    """
    conn = Connection().conn_back()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM stock.holding_stock_detail_current where `总持仓股数`  = 0")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


# #############################################TRACE_BACK#################################################

def get_initial_capital_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT `可用金额` FROM back.account")
        latest_data = pd.read_sql(sql, conn)
        capital = latest_data.iloc[-1, 0]
        return capital
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_holding_stock_detail_current_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("select * from back.holding_stock_detail_current")
        holding_stock_detail_current = pd.read_sql(sql, conn)
        return holding_stock_detail_current
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_holding_without_0_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("select * from back.holding_stock_detail_current where `总持仓股数` <> 0")
        holding_stock_detail_current = pd.read_sql(sql, conn)
        return holding_stock_detail_current
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_order_stock_detail_current_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT * FROM back.order_stock_detail_current")
        order_stock_detail_current = pd.read_sql(sql, conn)
        return order_stock_detail_current
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_order_stock_latest_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT * FROM back.order_stock_latest")
        order_stock_latest = pd.read_sql(sql, conn)
        return order_stock_latest
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_account_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT * FROM back.account ")
        account = pd.read_sql(sql, conn)
        return account
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_account_profit_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT * FROM back.account_profit_detail")
        account_profit = pd.read_sql(sql, conn)
        return account_profit
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_box_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT * FROM back.stocks_chosen_daily_50_new")
        box = pd.read_sql(sql, conn)
        return box
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_total_profit_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ("SELECT * FROM back.account_total_profit_detail")
        total_profit = pd.read_sql(sql, conn)
        return total_profit
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_order_stock_detail_history_back(stock_id, date):
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ('SELECT * FROM back.order_stock_detail_history where `证券代码` = ' + str(stock_id) + ' and `交易日` = CONCAT('+date+', "")')
        deal_history = pd.read_sql(sql, conn)
        return deal_history
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def get_bad_package_yesterday_back():
    """

    :param stock_id: 
    :return: newdata_close,newdata_open,newdata_high,newdata_low...(7*1)
    """
    conn = Connection().conn_back()
    try:
        sql = ('SELECT * FROM back.bad_package')
        deal_history = pd.read_sql(sql, conn)
        return deal_history
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_current_order_back():
    """
    # 删除当日委托表
    """
    conn = Connection().conn_back()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM back.order_stock_detail_current")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_current_deal_back():
    """
    # 删除当日成交表
    """
    conn = Connection().conn_back()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM back.deal_stock_detail_current")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_current_hold_0_back():
    """
    # 删除持仓表中卖空的股票
    """
    conn = Connection().conn_back()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM back.holding_stock_detail_current where `总持仓股数`  = 0")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


def delete_0():
    """
    # 删除数据更新进来为0的数据行
    """
    conn = Connection().conn_back()
    cur = conn.cursor()
    try:
        sql = ("DELETE FROM stock.fq_day_qfq where close = 0 or open = 0")
        cur.execute(sql)
        conn.commit()
    except Exception, e:
        print 'connect wrong'
        print e
    conn.close()


if __name__ == "__main__":
    # data = get_holding_stock_detail_current()
    # data = get_order_stock_detail_current()
    # print 'data', data
    # x = get_order_stock_detail_current()
    # print x
    # # delete_0()
    # import time
    # stock = '002352'
    # date = time.strftime('%Y%m%d', time.localtime(time.time()))
    # df = Get_DataFrame_0(stock, date)
    # # print type(df)
    # # print df.shape
    # print df.date[:9]
    print get_order_stock_detail_history_back('002265', '20170103')
