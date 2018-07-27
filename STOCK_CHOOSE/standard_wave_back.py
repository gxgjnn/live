# -*- coding: utf-8 -*-

from line import Line
import pandas as pd
import numpy as np


class Wave(Line):
    """
    寻找满足平衡条件的配对波峰波谷的price值，以预测未来买卖参考价，（最后只会返回一对波峰波谷），如果不存在则全部返回0
    第98行系数参数

    """

    def __init__(self, stock_id, date):
        super(Line, self).__init__(stock_id, date)
        df_s, cv_s, price_s, stop_dot_s = self.support_line()
        df_p, cv_p, price_p, stop_dot_p = self.pressure_line()
        # 矫正x轴
        if stop_dot_p > stop_dot_s:
            dif = stop_dot_p - stop_dot_s
            x_new = df_s.date + dif * self.ef
            df_s.date = x_new
        elif stop_dot_s > stop_dot_p:
            dif = stop_dot_s - stop_dot_p
            x_new = df_p.date + dif * self.ef
            df_p.date = x_new
        self.df_s = df_s
        self.cv_s = cv_s
        self.price_s = price_s
        self.stop_dot_s = stop_dot_s
        self.df_p = df_p
        self.cv_p = cv_p
        self.price_p = price_p
        self.stop_dot_p = stop_dot_p

    def data_provide(self):
        """

        :return: 
        wave_data: 按日期由远及近的波峰波谷的DataFrame
        data_ave_60: 60日均线数据集，时间由远及近
        data_ave_60_r: 60日均线数据集的回归线数据集，时间由远及近
        model: 60日均线回归线模型
        """
        # wave_data是波峰/波谷数据集组合，时间由远及近
        wave_data = pd.concat([self.df_s, self.df_p], axis=0)
        # 由远及近排序
        wave_data.sort_values(by=['date'], ascending=[True], inplace=True)
        stop_dot = max(self.stop_dot_p, self.stop_dot_s)
        # 60日均线数据集，时间由远及近
        data_ave_60 = self.angle_data(ave=60, stop_dot=stop_dot)
        # 通过回归线model，计算回归线数据集
        angle, a, b, model = self.line_model(data_ave_60)
        x = data_ave_60['date'].values.reshape(-1, 1)
        y = model.predict(x)
        # 60日均线数据集的回归线数据集，时间由远及近
        data_ave_60_r = pd.DataFrame({'date': np.array(list(data_ave_60['date'])), 'price': y})

        return wave_data, data_ave_60, data_ave_60_r, model

    def standard_wave(self):
        """
        (dis * 0.99) <= float(middle_y) <= (dis * 1.01):配对条件，其中0.99，1.01是可调参数
        :return: 
        e_pressure_fox 标准压力点
        e_support_fox 标准支撑点
        e_pressure_fox_smaller 最近已知波谷得出的压力点
        e_support_fox_larger 最近已知波峰得出的支撑点
        current_dis 距离当前日天数
        close_time_dis 平衡波点间距离天数（限制其天数）
        fox 满足标准波计算的所有波对，靠近k线图右侧的date,price的数据框，用于测试校验
        以上返回值均与所在60日均线值比较后返回结果，
        """
        wave_data, data_ave_60, data_ave_60_r, model = self.data_provide()
        # 计算满足标准涨跌配对的所有组合
        fox_date = []
        fox_price = []
        fox_time_dis = []
        if self.cv_p == 1:
            e_pressure_fox = self.price_p
        elif len(self.df_p) >= 2:
            e_pressure_fox = round((list(self.df_p.price)[-1] + list(self.df_p.price)[-2]) / 2, 2)
        else:
            e_pressure_fox = round(list(self.df_p.price)[-1] * 0.98, 2)

        if self.cv_s == 1:
            e_support_fox = self.price_s
        else:
            e_support_fox = round(min(list(self.df_s.price)[-1], list(self.df_s.price)[-2]), 2)

        e_pressure_fox_smaller = 0
        e_support_fox_larger = 0
        close_time_dis = 0
        current_dis = 0
        # print '*' * 30
        # print 'len(df_s):', len(self.df_s)
        # print 'len(df_p):', len(self.df_p)
        # print '*' * 30
        for i in range(len(self.df_s)):
            # 波谷价
            trough_dot_s = self.df_s['price'].iloc[i]
            # 波谷对应的x值
            date_dot_s = self.df_s['date'].iloc[i]
            # 波谷对应在60日均线上的price
            price_trough_bridge = data_ave_60.loc[data_ave_60.date < date_dot_s + self.ef,]
            price_trough_60 = list(price_trough_bridge.price.loc[price_trough_bridge.date > date_dot_s - self.ef,])[0]
            try:
                for j in range(len(self.df_p)):
                    peak_dot_p = self.df_p['price'].iloc[j]
                    date_dot_p = self.df_p['date'].iloc[j]
                    # 波峰对应在60日均线上的price
                    price_peak_bridge = data_ave_60.loc[data_ave_60.date < date_dot_p + self.ef, ]
                    price_peak_60 = list(
                        price_peak_bridge.price.loc[price_peak_bridge.date > date_dot_p - self.ef, ])[0]
                    # 保存配对波峰波谷
                    middle_x = (date_dot_p + date_dot_s) / 2
                    middle_y_r = model.predict(middle_x)
                    # 为了避免出现list out of the range,增加self.ef
                    middle_y_l_bridge = data_ave_60.loc[data_ave_60.date < middle_x + self.ef, ]
                    middle_y_l = list(middle_y_l_bridge.price.loc[middle_y_l_bridge.date > middle_x - self.ef, ])[0]
                    # 取两个price的中间价
                    middle_y = (middle_y_r + middle_y_l) / 2
                    dis = (trough_dot_s + peak_dot_p) / 2
                    # 因为计算的是收盘价，所以预估有2%的浮动
                    # print '*' * 30
                    # print '中间价dis:', dis
                    # print '中间价middle_y:', middle_y
                    # print '*' * 30
                    if (dis * 0.98) <= middle_y <= (dis * 1.02):
                        # ij_data是满足标准走势的波峰点合并波谷点的数据集
                        ij_data = pd.concat(
                            [pd.DataFrame(self.df_s.iloc[i, :]).T, pd.DataFrame(self.df_p.iloc[j, :]).T], 0)
                        ij_data.sort_values(by=['date'], ascending=[True], inplace=True)
                        # 为了计算距离天数
                        dis_ij = (ij_data.date.iloc[1] - ij_data.date.iloc[0]) / self.ef
                        # 去除小波段干扰,对dis_ij做限制，80相当于不做限制
                        if (trough_dot_s /
                                price_trough_60 <= 0.95) and (peak_dot_p / price_peak_60 >= 1.05) and (dis_ij < 80):
                            # print 'ij_data:', ij_data
                            fox_date.append(float(ij_data.date.iloc[-1]))
                            fox_price.append(float(ij_data.price.iloc[-1]))
                            fox_time_dis.append(dis_ij)
            except Exception, e:
                print e

        fox = pd.DataFrame({'date': fox_date, 'price': fox_price, 'time_dis': fox_time_dis})
        stop_dot = max(self.stop_dot_p, self.stop_dot_s)
        if fox.empty is False:
            # 计算标准涨跌价
            max_data = fox.loc[fox.date == max(fox.date), :]
            current_dis = stop_dot - list(max_data.date)[0] / self.ef
            # 一个x对应一个以上y值
            if len(max_data) > 1:
                closer_price = float(max_data.loc[max_data.time_dis == min(max_data.time_dis), 'price'])
                close_time_dis = min(max_data.time_dis)
            else:
                closer_price = float(fox.loc[fox.date == max(fox.date), 'price'])
                close_time_dis = float(fox.loc[fox.date == max(fox.date), 'time_dis'])
            # 计算后半段的中间价
            middle_dis = (stop_dot - max(fox.date) / self.ef) / 2 + max(fox.date) / self.ef
            close_date = middle_dis * self.ef
            # close_date = max(fox.date)
            # price_ave_60_predict_r = model.predict(close_date)
            # 这里不用回归线或两线中值的原因是，会对current_dis做限制，靠最新数据距离越近均线比均线回归线更有价值，以下同理
            data_ave_60_bridge = data_ave_60.loc[data_ave_60.date < close_date + self.ef, ]
            price_ave_60_predict_l = list(
                data_ave_60_bridge.price.loc[data_ave_60_bridge.date > close_date - self.ef, ])[0]
            # price_ave_60_predict = (price_ave_60_predict_r + price_ave_60_predict_l) / 2
            # closer_price 是离得最近的满足条件的波点的price
            if price_ave_60_predict_l > closer_price:
                e_pressure_fox = 2 * price_ave_60_predict_l - closer_price
            else:
                e_support_fox = 2 * price_ave_60_predict_l - closer_price
        # 如果fox是空的，选最大值取对应值做e_support_fox/e_pressure_fox
        else:
            max_peak_price = max(np.array(self.df_p.price))
            max_peak_data = np.array(self.df_p.date.loc[self.df_p.price == max_peak_price, ])[-1]
            max_peak_data_dis = (stop_dot - max_peak_data / self.ef) / 2 + max_peak_data / self.ef
            x = max_peak_data_dis * self.ef
            x_bridge = data_ave_60.loc[data_ave_60.date < x + self.ef, ]
            middle_peak_price_l = list(x_bridge.price.loc[x_bridge.date > x - self.ef, ])[0]
            e_support_fox_bridge = 2 * middle_peak_price_l - max_peak_price
            if e_support_fox_bridge < self.ave_price_60[0]:
                print 'peak_max'
                e_support_fox = e_support_fox_bridge * 1.03

            min_trough_price = min(np.array(self.df_s.price))
            min_trough_data = np.array(self.df_s.date.loc[self.df_s.price == min_trough_price, ])[-1]
            min_trough_data_dis = (stop_dot - min_trough_data / self.ef) / 2 + min_trough_data / self.ef
            x = min_trough_data_dis * self.ef
            x_bridge = data_ave_60.loc[data_ave_60.date < x + self.ef, ]
            middle_trough_price_l = list(x_bridge.price.loc[x_bridge.date > x - self.ef, ])[0]
            e_pressure_fox_bridge = 2 * middle_trough_price_l - min_trough_price
            # else的情况不考虑
            if e_pressure_fox_bridge > self.ave_price_60[0]:
                print 'trough_min'
                e_pressure_fox = e_pressure_fox_bridge

        # 计算最近标准涨跌价
        closest_price = wave_data.price.iloc[-1]
        closest_date_0 = wave_data.date.iloc[-1]
        middle_dis = (stop_dot - closest_date_0 / self.ef) / 2 + closest_date_0 / self.ef
        closest_date = middle_dis * self.ef
        # price_ave_60_predict_r = model.predict(closest_date)
        data_ave_60_bridge = data_ave_60.loc[data_ave_60.date < closest_date + self.ef, ]
        price_ave_60_predict_l = list(
            data_ave_60_bridge.price.loc[data_ave_60_bridge.date > closest_date - self.ef, ])[0]
        # price_ave_60_predict = (price_ave_60_predict_r + price_ave_60_predict_l) / 2
        if price_ave_60_predict_l > closest_price:
            e_pressure_fox_smaller = 2 * price_ave_60_predict_l - closest_price

        else:
            e_support_fox_larger = 2 * price_ave_60_predict_l - closest_price

        return e_pressure_fox, e_support_fox, e_pressure_fox_smaller, e_support_fox_larger, current_dis\
            , close_time_dis, fox

    def paint_paint_line(self):
        """

        :return: 波峰波谷点和所在60日回归线图形
        """
        wave_data, data_ave_60, data_ave_60_r, model = self.data_provide()
        print 'stop_dot:\n', max(self.stop_dot_p, self.stop_dot_s)
        # 作图
        self.paint_line(wave_data, data_ave_60)


if __name__ == "__main__":
    stock = '300011'
    dates = '20170116'
    obj = Wave(stock, dates)
    # a,b,c,d= obj.data_provide()
    # print 'wave_data:',a
    # print 'data_ave_60:',b
    # print 'data_ave_60_r:',c
    # print 'model:',d
    e_pressure = obj.price_p
    e_support = obj.price_s
    aa, bb, c, d, ee, f, ox = obj.standard_wave()
    print '*' * 30
    print 'e_pressure:', e_pressure
    print 'e_support:', e_support
    print 'e_pressure_fox', aa
    print 'e_support_fox', bb
    print 'e_pressure_fox_smaller', c
    print 'e_support_fox_larger', d
    print 'current_dis', ee
    print 'close_time_dis', f
    print 'fox', ox
    print '*' * 30
    obj.paint_paint_line()