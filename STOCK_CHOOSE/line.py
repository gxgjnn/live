# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import math
from line_angle import Angle
from utils import data_process


class Line(Angle):
    """
    def __support_line() 和 def __pressure_line()
        i:序列断点起始值 
        j:断点后起始连续值，当前参数为5，连续值小于等于5的最小值，不列入波谷/峰内，是一个可调参数
        cov:变异系数，到回归线的平均标准距离 与 到最低/最高平行线距离的比值 ，越接近1 差异越小，说明有明显的支撑线/压力线，
            当前支撑位为0.5，，压力位为0.4是一个可调参数
        angle:def __support_line()中，当前参数为0，要求支撑线角度要大于(0，30)，def __pressure_line()中，当前参数为(-10，30)，
            压力线越平稳越好，是一个可调参数
        len(trough/peak):波谷/波峰的个数，当前参数为2，个数大于2是存在cov的前提之一，否则，顺延x（60，90，120，150）
        price_1:波谷/波峰的拟合线预测最新价，因为有弹性，
            因此设置为max((0.98 * reg.predict(len(data) * self.ef),reg.predict(x_low[-1])),其中0.98为可调测试参数
    def __support_line() 和 def __pressure_line()代码不能合并，计算变异系数的差异所致
    def support_line() 和 def pressure_line()
        len(order_up/low):order_low/order_up的长度目前是以60天为x值计算位的为(5,45)，90天的为(7,60)，120天的为(10,80)，
                        150天的为(14,100),目的是过滤那些涨跌不平衡的股票，一旦过滤，df=pd.DataFrame(),cv = -1,
                        括号内的都是可调参数
        len(list(data0.close[:125].loc[data0.close == 0])) <= 5：考虑停牌天数对计算60日均线的合理性，目前参数为
                                                                [:135],[:180],[:210],[:210],其中最后一位要改
                                                                <=15,<=30,<=30,<=0,其中后两位要改
    """
    def __init__(self, stock_id):
        super(Line, self).__init__(stock_id)
        # "divide by zero" or "divide by NaN"
        # np.seterr(divide='ignore', invalid='ignore')

    def __support_line(self, order_low, data):
        """
        :param data:data = list(self.df.low[0:60]),其中60会变
        :param order_low: list of different days order id given below
        :return: DataFrame of support_line , cv is the standard whether support_line is true line or not 
                [cv == 0 is fake line,cv == 1 is true line ,cv == -1 is emergent imbalance in list order_low ]
        """
        np.seterr(divide='ignore', invalid='ignore')
        # 算出波谷的回归线
        trough = []
        x_low = []
        i = order_low[0]
        size = len(order_low)
        j = 1
        while j < size:
            try:
                # print 'i,j', i, j
                if all(np.in1d(np.array(range(i, i + j, 1)), np.array(order_low))) and (
                        order_low[order_low.index(i + j - 1) + 1] - order_low[order_low.index(i + j - 1)] != 1):
                    # print 'i', i
                    # print 'j', j
                    d = []
                    next_i = order_low[order_low.index(i + j - 1) + 1]
                    if j > 4:
                        for k in range(i, i + j):
                            d.append(data[k])
                            index = d.index(min(d))
                            # print 'index',index
                            # print 'index+i', index+i
                            # print list(low)[index+i]
                            # print d
                        # + 1 是因为(index + i + 1)!=0
                        x_low.append((index + i + 1) * self.ef)
                        trough.append(min(d))

                    i = next_i
                    j = 1
                    continue
            except Exception, e:
                pass

            try:
                # print i, j
                if all(np.in1d(np.array(range(i, i + j, 1)), np.array(order_low))) and (order_low[-1] == i + j - 1):
                    # print i
                    # print j
                    d = []
                    if j > 4:
                        for k in range(i, i + j):
                            d.append(data[k])
                            index = d.index(min(d))
                        # print d
                        x_low.append((index + i + 1) * self.ef)
                        trough.append(min(d))
                        # i = order_low[j]
                        # j = 1
                    break
            except Exception, e:
                pass
            j = j + 1

        # print 'trough.append(min(d))', trough

        # 计算阈值（变异系数）
        # dis = 所有波谷价到波谷回归线的距离的平方，和， / n  ，开根 - --就是标准差，
        trough_data = pd.DataFrame({'date': x_low, 'price': np.array(trough)})
        if trough_data.empty:
            trough_data = pd.DataFrame()
            cov = 0
            predict_price = 0
            # print "trough_data is empty"
            return trough_data, cov, predict_price

        angle, a, b, reg = self.line_model(trough_data)
        predict_price_0 = reg.predict(x_low[-1])
        # 2%的幅度我觉的合理
        predict_price_1 = reg.predict((len(data)+1) * self.ef)
        predict_price = round(max(predict_price_0, predict_price_1)[0], 2)

        # print 'support_predict_price', predict_price
        # print 'support_line_angle:', angle
        # 求出peak到回归线的距离的标准差standard_dis
        # 已知斜率和截距求点线距离| kx1 - y1 + b | / √[k²+（-1）²]
        dis = []
        for (i, j) in zip(trough_data['date'], trough_data['price']):
            distance = pow(abs(a*i-j+b)/math.sqrt(a*a+1), 2)
            dis.append(distance)
        standard_dis = math.sqrt(sum(dis)/len(trough))
        # print 'standard_dis',standard_dis

        # 求出经过波谷最低点的直线
        y0 = min(trough_data['price'])
        x0 = max(trough_data.loc[trough_data.price == y0, 'date'])
        b2 = y0 - x0*a
        # ave = 所有波谷点到该直线的距离的平均数
        ave = []
        for (i, j) in zip(trough_data['date'], trough_data['price']):
            distance = abs(a*i-j+b2)/math.sqrt(a*a+1)
            ave.append(distance)

        ave_dis = sum(ave) / (len(trough) - 1)
        # 变异系数(coefficient of variation)
        cov = (standard_dis / ave_dis)

        # print 'ave',sum(ave),len(ave),ave
        # print 'ave_dis',ave_dis
        # print 'support_cv:', cov
        # 阈值设定看测试结果,变异系数越接近1越好（不可能超过1）;波谷个数大于2才有说明价值，2个容易曲解走势
        if (cov > 0.5) and (0 < angle < 30) and (len(trough) > 2) and (self.ave_price_60[0] > predict_price):
            cov = 1
        else:
            cov = 0
        return trough_data, cov, predict_price

    def support_line(self):
        """
        cv = -1的理由1、停牌时间太久，影响60日均线值的准确度，2、最高价在60日均线下方的k线过多或过少
        为了找到标准支撑线，从60天按每30天顺延至150天，如此操作支撑线可靠性更高,但是范围越大，数据（cv,angle）会越好，反倒不利于交易
        :return: DataFrame of support_line  &  cv is the standard whether support_line is true line or not 
                [cv == 0 is fake line,cv == 1is true line ,cv == -1 is emergent imbalance in list order_low ]
        """
        # 为了考虑停牌天数对计算60日均线的合理性问题
        data0 = data_process.Get_DataFrame_0(self.stock_id, self.date)

        data = list(self.df.low[0:60])
        data.reverse()
        order_low = []
        # 60天内所有最高价小于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
        ave_price_60_0 = self.ave_price_60[:60]
        ave_price_60_0.reverse()
        df_high_0 = list(self.df.high[:60])
        df_high_0.reverse()
        # 为了计算60日均线的合理性问题，近120个k线内允许15个停牌k线
        if len(list(data0.close[:150].loc[data0.close == 0])) <= 30:
            for i in range(0, 60):
                if df_high_0[i] < ave_price_60_0[i]:
                    order_low.append(i)
            if 5 < len(order_low) < 45:
                df_0, cv_0, price_0 = self.__support_line(order_low, data)
            else:
                df_0 = pd.DataFrame()
                cv_0 = -1
                price_0 = 0
        else:
            df_0 = pd.DataFrame()
            cv_0 = -1
            price_0 = 0

        if cv_0 == 0:
            data = list(self.df.low[0:90])
            data.reverse()
            order_low = []
            # 90天内所有最高价小于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
            ave_price_60_0 = self.ave_price_60[:90]
            ave_price_60_0.reverse()
            df_high_0 = list(self.df.high[:90])
            df_high_0.reverse()
            # 为了计算60日均线的合理性问题，近180个k线内允许30个停牌k线
            if len(list(data0.close[:200].loc[data0.close == 0])) <= 50:
                for i in range(0, 90):
                    if df_high_0[i] < ave_price_60_0[i]:
                        order_low.append(i)
                if 7 < len(order_low) < 60:
                    df_1, cv_1, price_1 = self.__support_line(order_low, data)
                else:
                    df_1 = pd.DataFrame()
                    cv_1 = 0
                    price_1 = 0
            else:
                df_1 = pd.DataFrame()
                cv_1 = -1
                price_1 = 0

            if cv_1 == 0:
                data = list(self.df.low[0:120])
                data.reverse()
                order_low = []
                # 120天内所有最高价小于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
                ave_price_60_0 = self.ave_price_60[:120]
                ave_price_60_0.reverse()
                df_high_0 = list(self.df.high[:120])
                df_high_0.reverse()
                # 为了计算60日均线的合理性问题，近180个k线内允许30个停牌k线
                if len(list(data0.close[:250].loc[data0.close == 0])) <= 70:
                    for i in range(0, 120):
                        if df_high_0[i] < ave_price_60_0[i]:
                            order_low.append(i)
                    if 10 < len(order_low) < 70:
                        df_2, cv_2, price_2 = self.__support_line(order_low, data)
                    else:
                        df_2 = pd.DataFrame()
                        cv_2 = 0
                        price_2 = 0
                else:
                    df_2 = pd.DataFrame()
                    cv_2 = -1
                    price_2 = 0

                if cv_2 == 0:
                    data = list(self.df.low[0:150])
                    data.reverse()
                    order_low = []
                    # 120天内所有最高价小于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
                    ave_price_60_0 = self.ave_price_60[:150]
                    ave_price_60_0.reverse()
                    df_high_0 = list(self.df.high[:150])
                    df_high_0.reverse()
                    # 为了计算60日均线的合理性问题，近210个k线内允许0个停牌k线，目前数据所致
                    if len(list(data0.close[:300].loc[data0.close == 0])) <= 90:
                        for i in range(0, 150):
                            if df_high_0[i] < ave_price_60_0[i]:
                                order_low.append(i)
                        # 如果超过75了不符合中期整体向上的理论
                        if 14 < len(order_low) < 75:
                            df_3, cv_3, price_3 = self.__support_line(order_low, data)
                        else:
                            df_3 = pd.DataFrame()
                            cv_3 = -1
                            price_3 = 0
                    else:
                        df_3 = pd.DataFrame()
                        cv_3 = -1
                        price_3 = 0
                    stop_dot = 150
                    # print 'three150'
                    return df_3, cv_3, price_3, stop_dot

                else:
                    stop_dot = 120
                    # print 'two120'
                    return df_2, cv_2, price_2, stop_dot

            else:
                stop_dot = 90
                # print 'one90'
                return df_1, cv_1, price_1, stop_dot

        else:
            stop_dot = 60
            # print 'zero60'
            return df_0, cv_0, price_0, stop_dot

    def __pressure_line(self, order_up, data):
        """
        :param data:data = list(self.df.high[0:60]),其中60会变
        :param order_up: list of different days order id given by def pressure_line
        :return: DataFrame of pressure_line , cv is the standard whether pressure_line is true line or not 
                [cv == 0 is fake line,cv == 1is true line ,cv == -1 is emergent imbalance in list order_up ]
        """
        np.seterr(divide='ignore', invalid='ignore')
        # 算出波峰的回归线
        peak = []
        x_up = []
        i = order_up[0]
        size = len(order_up)
        j = 1
        while j < size:
            try:
                # print i, j
                if all(np.in1d(np.array(range(i, i + j, 1)), np.array(order_up))) and (
                        order_up[order_up.index(i + j - 1) + 1] - order_up[order_up.index(i + j - 1)] != 1):
                    # print '*'*30
                    # print 'i', i
                    # print 'j', j
                    # print '*'*30
                    d = []
                    next_i = order_up[order_up.index(i + j - 1) + 1]
                    if j > 4:
                        for k in range(i, i + j):
                            d.append(data[k])
                            index = d.index(max(d))
                            # print 'index',index
                            # print 'index+i', index+i
                            # print list(low)[index+i]
                            # print d
                        x_up.append((index + i + 1) * self.ef)
                        peak.append(max(d))

                    i = next_i
                    j = 1
                    continue
            except Exception, e:
                pass
            try:
                # print i, j
                if all(np.in1d(np.array(range(i, i + j, 1)), np.array(order_up))) and (order_up[-1] == i + j - 1):
                    # print i
                    # print j
                    d = []
                    if j > 5:
                        for k in range(i, i + j):
                            d.append(data[k])
                            index = d.index(max(d))
                            # print d
                        x_up.append((index + i + 1) * self.ef)
                        peak.append(max(d))
                        # i = order_low[j]
                        # j = 1
                    break
            except Exception, e:
                pass
            j = j + 1

        # print 'peak.append(max(d))', peak

        # 计算阈值（变异系数）
        # dis = 所有波峰价到波峰回归线的距离的平方，和， / n  ，开根 - --就是标准差，
        peak_data = pd.DataFrame({'date': x_up, 'price': np.array(peak)})
        if peak_data.empty:
            peak_data = pd.DataFrame()
            cov = 0
            predict_price = 0
            # print "peak_data is empty"
            return peak_data, cov, predict_price

        angle, a, b, reg = self.line_model(peak_data)
        predict_price_0 = reg.predict(x_up[-1])
        # 角度越大predict_price_1越比predict_price_0大，不保守可以增加0.98
        predict_price_1 = 0.98 * reg.predict(len(data) * self.ef)
        predict_price = round(max(predict_price_0, predict_price_1)[0], 2) - 0.02
        # print 'pressure_predict_price', predict_price
        # print 'pressure_line_angle:', angle
        # peak到回归线的距离的标准差standard_dis
        # 已知斜率和截距求点线距离| kx1 - y1 + b | / √[k²+（-1）²]
        dis = []
        for (i, j) in zip(peak_data['date'], peak_data['price']):
            distance = pow(abs(a*i-j+b)/math.sqrt(a*a+1), 2)
            dis.append(distance)
        standard_dis = math.sqrt(sum(dis)/len(peak))
        # print 'standard_dis',standard_dis

        # 求出经过波峰最高点的直线
        y0 = max(peak_data['price'])
        # len(x0)>1,取较小值是远离标准位线，更有说明性
        x0 = min(peak_data.loc[peak_data.price == y0, 'date'])
        b2 = y0 - x0*a
        # ave = 所有波峰点到该直线的距离的平均数
        ave = []
        for (i, j) in zip(peak_data['date'], peak_data['price']):
            distance = abs(a*i-j+b2)/math.sqrt(a*a+1)
            ave.append(distance)

        ave_dis = sum(ave) / (len(peak) - 1)
        # 变异系数
        cov = (standard_dis / ave_dis)
        # 阈值设定看测试结果,变异系数越接近1越好（不可能超过1），波峰个数大于2才有说明价值，2个容易曲解走势,对压力线，角度不过于限制
        if (cov > 0.4) and (-10 < angle < 30) and (len(peak) > 2) and (self.ave_price_60[0] < predict_price):
            cov = 1
        else:
            cov = 0
        return peak_data, cov, predict_price

    def pressure_line(self):
        """
        cv = -1的理由1、停牌时间太久，影响60日均线值的准确度，2、最低价在60日均线上方的k线过多或过少
        为了找到标准压力线，从60天按每30天顺延至150天(一年交易日)，如此操作压力线可靠性更高
        :return: DataFrame of pressure_line , cv is the standard whether pressure_line is true line or not 
                [cv == 0 is fake line,cv == 1is true line ,cv == -1 is emergent imbalance in list order_up ]
        """
        # 为了考虑停牌天数对计算60日均线的合理性问题
        data0 = data_process.Get_DataFrame_0(self.stock_id, self.date)

        data = list(self.df.high[0:60])
        data.reverse()
        order_up = []
        # 60天内所有最低价大于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
        ave_price_60_0 = self.ave_price_60[:60]
        ave_price_60_0.reverse()
        df_low_0 = list(self.df.low[:60])
        df_low_0.reverse()
        # 为了计算60日均线的合理性问题，近120个k线内允许5个停牌k线
        if len(list(data0.close[:150].loc[data0.close == 0])) <= 30:
            for i in range(0, 60):
                if df_low_0[i] > ave_price_60_0[i]:
                    order_up.append(i)
            # 为什么要限制，1、k线走势不平衡顺延2、'else'3、比45再大点60日均线下方的点0~13个点的波谷点难取
            if 5 < len(order_up) < 45:
                df_0, cv_0, price_0 = self.__pressure_line(order_up, data)
            else:
                df_0 = pd.DataFrame()
                cv_0 = -1
                price_0 = 0
        else:
            df_0 = pd.DataFrame()
            cv_0 = -1
            price_0 = 0

        if cv_0 == 0:
            data = list(self.df.high[0:90])
            data.reverse()
            order_up = []
            # 90天内所有最低价大于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
            ave_price_60_0 = self.ave_price_60[:90]
            ave_price_60_0.reverse()
            df_low_0 = list(self.df.low[:90])
            df_low_0.reverse()
            # 为了计算60日均线的合理性问题，150天内允许30天的停牌天数
            if len(list(data0.close[:200].loc[data0.close == 0])) <= 50:
                for i in range(0, 90):
                    if df_low_0[i] > ave_price_60_0[i]:
                        order_up.append(i)
                if 20 < len(order_up) < 70:
                    df_1, cv_1, price_1 = self.__pressure_line(order_up, data)
                else:
                    df_1 = pd.DataFrame()
                    cv_1 = 0
                    price_1 = 0
            else:
                df_1 = pd.DataFrame()
                cv_1 = -1
                price_1 = 0

            if cv_1 == 0:
                data = list(self.df.high[0:120])
                data.reverse()
                order_up = []
                # 120天内所有最低价大于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
                ave_price_60_0 = self.ave_price_60[:120]
                ave_price_60_0.reverse()
                df_low_0 = list(self.df.low[:120])
                df_low_0.reverse()
                # 为了计算60日均线的合理性问题，210个k线内允许30个k线的停牌，目前受到数据限制上限就是30【增加数据量后要改写的】
                if len(list(data0.close[:250].loc[data0.close == 0])) <= 70:
                    for i in range(0, 120):
                        if df_low_0[i] > ave_price_60_0[i]:
                            order_up.append(i)
                    if 35 < len(order_up) < 85:
                        df_2, cv_2, price_2 = self.__pressure_line(order_up, data)
                    else:
                        df_2 = pd.DataFrame()
                        cv_2 = 0
                        price_2 = 0
                else:
                    df_2 = pd.DataFrame()
                    cv_2 = -1
                    price_2 = 0

                if cv_2 == 0:
                    data = list(self.df.high[0:150])
                    data.reverse()
                    order_up = []
                    # 90天内所有最低价大于60日均线价的数据，不用担心粘连60日均线的K线影响波峰波谷的计算
                    ave_price_60_0 = self.ave_price_60[:150]
                    ave_price_60_0.reverse()
                    df_low_0 = list(self.df.low[:150])
                    df_low_0.reverse()
                    # 为了计算60日均线的合理性问题，210个k线内允许0个k线的停牌
                    if len(list(data0.close[:300].loc[data0.close == 0])) <= 90:
                        for i in range(0, 150):
                            if df_low_0[i] > ave_price_60_0[i]:
                                order_up.append(i)
                        if 45 < len(order_up) < 105:
                            df_3, cv_3, price_3 = self.__pressure_line(order_up, data)
                        else:
                            df_3 = pd.DataFrame()
                            cv_3 = -1
                            price_3 = 0
                    else:
                        df_3 = pd.DataFrame()
                        cv_3 = -1
                        price_3 = 0
                    stop_dot = 150
                    # print 'three150'
                    return df_3, cv_3, price_3, stop_dot

                else:
                    stop_dot = 120
                    # print 'two120'
                    return df_2, cv_2, price_2, stop_dot

            else:
                stop_dot = 90
                # print 'one90'
                return df_1, cv_1, price_1, stop_dot

        else:
            stop_dot = 60
            # print 'zero60'
            return df_0, cv_0, price_0, stop_dot

    def cross_dot(self, date):
        """
    
        :param date: 20160101-20171222的数据，（433-60）以内
        :return: list,按日期由远及近
        """
        cross = []
        # 日均线和60日均线交点数据
        for i in range(0, date):
            if self.df.low[i] <= self.ave_price_60[i] <= self.df.high[i]:
                cross.append(self.ave_price_60[i])
        cross.reverse()
        return cross

if __name__ == "__main__":
    stock = '300011'
    dates = '20170116'
    object_ = Line(stock)
    df, cv, price, dot = object_.pressure_line()
    print 'df_p',df
    print 'e_pressure:', price
    print 'cv_p:', cv
    print 'peak_data:\n', df
    print '*'*30
    df, cv, price, dot = object_.support_line()
    print 'df_s',df
    print 'e_support:', price
    print 'cv_s:', cv
    print 'trough_data:\n', df