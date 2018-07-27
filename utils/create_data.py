# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# 目前从20160101截至20171222，433个交易日，date暂时取300


def ave_data_create(data, ave, date=300):
    """
    不考虑中间停牌没有数据的情况，数据向后顺延
    :param data: 一个stock_id的收盘价数据集，Series
    :param ave: 均线值
    :param date: 计算300个值
    :return: 60日均线值*300的list，对应的日期由近及远
    """

    ave_list = []
    for i in range(0, date):
        ave_price = data[i:ave + i].mean()
        ave_list.append(round(ave_price, 2))
    return ave_list


def ave_data_draw(ef, data, ave, dt=301):
    """
    
    :param ef: 根据196个交易日内，长宽比等于价格差与天数乘以系数（ef）比，为了计算自变量，来替换时间序列，好得出想要的角度
    :param data: 一个stock_id的收盘价数据集，Series
    :param ave: 均线值
    :param dt: 计算300个值
    :return: dt-1个点的点图，按照日期由远及近，验证请看同花顺
    """

    dat = []
    # range根据def Ave_data_create(ave,date = 60)的第二个参数变化
    for i in range(1, dt):
        dat.append(ef * i)

    ave_price = ave_data_create(data, ave)
    ave_price.reverse()
    df1 = pd.DataFrame({'date': dat, 'price': np.array(ave_price)})

    ave_price0 = ave_data_create(data, 1)
    ave_price0.reverse()
    df0 = pd.DataFrame({'date': dat, 'price': np.array(ave_price0)})
    # 画图
    # 1.60日均线
    plt.scatter(df1['date'], df1['price'], color='blue')
    # 1.真实的点
    plt.plot(df0['date'], df0['price'], color='red')
    plt.show()

if __name__ == "__main__":
    # ave_data_test(ave = 60, stock_id='600017.XSHG')
    from utils import data_process
    stock_id = '002010'
    df = data_process.Get_DataFrame(stock_id)
    if len(df.close) > 360:
        if len(df.high) >= 196:
            dif = max(df.high[:196]) - min(df.low[:196])
            ef1 = round((36 / 12.5) * dif / 196, 4)
            ave_data_draw(ef1, df.close, 60)
        else:
            print 'len(df.high) is', len(df.high)
            print 'picture incorrect because of ef value'
    else:
        print 'len(df.close) is', len(df.close)
        print 'picture incorrect because of  len(df.close) value'