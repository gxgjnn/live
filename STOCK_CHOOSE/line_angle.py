# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from sklearn import linear_model
import matplotlib.pyplot as plt
import math
from utils import data_process
from utils import create_data
import time


class Angle(object):

    def __init__(self, stock_id, date=time.strftime('%Y%m%d', time.localtime(time.time()))):
        self.date = date
        self.stock_id = stock_id
        self.df = data_process.Get_DataFrame(self.stock_id, self.date)
        if len(self.df.high) >= 196:
            dif = max(self.df.high[:196]) - min(self.df.low[:196])
            # 根据196个交易日内，长宽比等于价格差与天数乘以系数（ef）比，为了计算自变量，来替换时间序列，好得出想要的角度
            # 切记，要个股196至200天的最高与最低的数据
            ef = round((36 / 12.5) * dif / 196, 4)
        else:
            # 如果数据不够的情况，为使角度变大
            ef = 0.0000001
        self.ef = ef
        # 不考虑数据不够的情况，比较少
        self.ave_price_60 = create_data.ave_data_create(self.df.close, 60)
        self.ave_price_5 = create_data.ave_data_create(self.df.close, 5)

    def angle_data(self, ave=60, stop_dot=50):
        """
        
        :return: DataFrame (for create line_model below,60 for angle enough)
        """

        date = []
        for i in range(1, stop_dot+1):
            date.append(self.ef * i)
        ave_price = create_data.ave_data_create(self.df.close, ave)[:stop_dot]
        ave_price.reverse()
        data = pd.DataFrame({'date': date, 'price': np.array(ave_price)})
        # df = pd.DataFrame({'square_feet':[150,200,250,300,350,400,600],'price':[150,200,250,300,350,400,600]})
        return data

    @staticmethod
    def line_model(data):
        """

        :param data: data from def angle_data
        :return: angle,a,b,reg(角度,斜率、截距,线性回归模型)
        """
        # 建立线性回归模型
        reg = linear_model.LinearRegression()
        # 拟合
        reg.fit(data['date'].values.reshape(-1, 1), data['price'])  # 注意此处.reshape(-1, 1)，因为X是一维的！

        # 不难得到直线的斜率、截距
        # 要求回归系数
        a, b = reg.coef_, reg.intercept_
        # 得出角度
        angle = math.degrees(math.atan(a))
        return angle, a, b, reg

    def pre_price_date(self, reg, x, y):
        """
        
        :param reg: line_model from def line_model
        :param x: 斜率
        :param y: 截距
        :return: price(y) mostly
        """
        a, b = reg.coef_, reg.intercept_
        # 方式1：根据直线方程计算的价格
        # print(model.a * area + model.b)
        # 方式2：根据predict方法预测的价格
        if x != 0:
            price = reg.predict(x*self.ef)
            return price
        if y != 0:
            date = (y - b) / a
            return date

    @staticmethod
    def paint_line(data_dot, data_line):
        """
        
        :return: 近60天真实线和60日均线的图
        """
        # data = self.angle_data()
        #  angle, a, b, model = self.line_model(data_line)
        # 画图
        # 1.日线
        plt.scatter(data_dot['date'], data_dot['price'], color='blue')
        # 2.60日均线
        plt.plot(data_line['date'], data_line['price'], color='red', linewidth=4)
        plt.grid()
        plt.legend(['3', '4', '5'], loc='upper right')
        plt.show()

if __name__ == "__main__":

    stock = '002599'
    date_start = '20170118'
    obj = Angle(stock, date_start)
    # print df
    dat = obj.angle_data()
    dat2 = obj.angle_data(ave=1)
    print obj.line_model(dat)
    obj.paint_line(dat2, dat)