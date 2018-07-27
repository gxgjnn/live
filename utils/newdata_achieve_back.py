# -*- coding: utf-8 -*-

import Queue
import threading
import os
import datetime
import tushare as ts
from sqlalchemy import create_engine
from sqlalchemy import types
import time
import socket
import pandas as pd
# 数据库要定期更新，不包括所取时间段外停牌的股票


# 创建mysql数据库引擎，便于后期链接数据库
# mysql_info = {'host': '172.16.10.13', 'port': 3307, 'user': 'root', 'password': '123456', 'db': 'stock',
#             'charset': 'utf8'}
mysql_info = {'host': 'localhost', 'port': 3306, 'user': 'root', 'db': 'stock', 'password': '123456', 'charset': 'utf8'}

engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=%s' % (mysql_info['user'], mysql_info['password'],
                                                                      mysql_info['host'], mysql_info['port'],
                                                                      mysql_info['db'], mysql_info['charset']),
                       echo=False)


def get_stock_basics():
    e = 0
    try:
        stock_basics = ts.get_stock_basics()
    except Exception, e:
        stock_basics = pd.DataFrame()
        pass
    return e, stock_basics
# 获取所有股票数据，利用股票代码获取复权数据

error, stock_basics = get_stock_basics()
while error != 0:
    time.sleep(150)
    error, stock_basics = get_stock_basics()
# stock_basics = ts.get_stock_basics()

# stock_basics.columns
# stock_basics.to_csv('stock_basic_list.csv')

# 获取数据库现有数据的时间日期


def get_old_date():
    con = engine.connect()
    sql1 = 'show tables;'
    tables = con.execute(sql1)
    if ('fq_day_qfq',) not in tables:
        date_old = datetime.date(2016, 1, 1)
        return date_old
    sql2 = 'select max(date) from fq_day_qfq;'
    date_old = con.execute(sql2).fetchall()[0][0].date()
    if date_old < datetime.date.today() - datetime.timedelta(1):
        return date_old
    else:
        con.close()
        print('今天已经获取过数据，不需重新获取')
        # os._exit(1)

# 声明队列，用于存取股票以代码数据，以便获取复权明细
stock_code_queue = Queue.Queue(0)
for code in stock_basics.index:
    stock_code_queue.put(code)

# len(stock_basics.index)
# stock_code_queue.qsize()
# stock_code_queue.queue.clear()

type_fq_day = {'code': types.CHAR(6), 'open': types.FLOAT, 'high': types.FLOAT, 'close': types.FLOAT,
               'low': types.FLOAT, 'amount': types.FLOAT, 'factor': types.FLOAT}


def process_data(task_queue):
    """
    
    :param old_date: 
    :param task_queue: 
    :return: 获取除权数据
    """
    socket.setdefaulttimeout = 10
    # queueLock.acquire()
    while not task_queue.empty():
        data = task_queue.get()
        # time.sleep(8)
        print ("正在获取%s;数据还有%s条:" %(data, task_queue.qsize()))
        # queueLock.release()
        # date_begin = old_date + datetime.timedelta(1)
        # date_end = datetime.date.today()
        date_end = datetime.date(2018, 2, 13)
        try:
            # print "data:"
            # print data
            # qfq_day = ts.get_h_data(data, start=str(date_begin), end=str(date_end), autype='qfq', drop_factor=False)
            qfq_day = ts.get_h_data(data, start=str('2018-04-13'), end=str('2018-04-13'), autype=None, drop_factor=False)
            # date_end = datetime.date(2018, 2, 9)
            # time.sleep(5)
            # print "qfq_day.shape", qfq_day.shape
            qfq_day['code'] = data
            # print "before"
            qfq_day.to_sql('fq_day_qfq', engine, if_exists='append', dtype=type_fq_day)
            # print "after"
            task_queue.task_done()
        except:
            print 'system busy'
            time.sleep(150)
            task_queue.put(data)
            # time.sleep(2)# 如果数据获取失败，将该数据重新存入到队列，便于后期继续执行
    # else:
    #     queueLock.release()


class get_qfq(threading.Thread):
    """
    # 重写线程类，用户获取数据
    """
    def __init__(self, name, queue, date_begin):
        threading.Thread.__init__(self)
        self.name = name
        self.queue = queue
        self.begin = date_begin

    def run(self):
        process_data(self.begin, self.queue)
        print("Exiting " + self.name)


if __name__ == "__main__":
    # get_qfq = get_qfq()
    # 声明线程锁
    # queueLock = threading.Lock()

    # if stock_code_queue.empty()==False:
    #     old_date = datetime.date(2017,1,1)
    # else:
    #     old_date = get_old_date()

    # old_date0 = get_old_date()
    process_data(stock_code_queue)

    # threads = []
    # for i in range(10):
    #     thread = get_qfq('thread' + str(i), stock_code_queue, old_date)
    #     thread.start()
    #     threads.append(thread)
    # for thread in threads:
    #     thread.join()

