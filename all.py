
# #################买入不报警，异常卖出要报警
# def alarm（stock, *arg）  # 红黄蓝绿预警，紧急度依旧降低
#
# def research（stock）  # 需要立即解决的卖不掉的问题持仓股
#
# def recalculate(stock)：
#     price_most：当日最高价，price_least：当日最低价, ave_60：60
#     日均线价，ave_60_yesterday：昨日60日均线价，price_most_yesterday:昨日收盘最高价, price_least_yesterday:昨日收盘最低价
#     if price_most > ave_60 & price_least < ave_60 & price_most_yesterday < ave_60_yesterday  # 在60日均线下方，k线触碰60日均线，确定最新的波谷后重新计算二次买卖价
#         重新计算卖价等值
#     if price_most > ave_60 & price_least < ave_60 & price_least_yesterday > ave_60_yesterday  # 在60日均线上方，k线触碰60日均线，确定最新的波谷后重新计算二次买卖价
#         重新计算
#         if close_price - ave_60 < 0
#             抛掉成本额，留下盈利额
#             buy（stock）
#             # 这个条件说明，一个股票可以在标准价位变化后，重复买入
#         加一个条件，计算recalculate后计算与上一次recalculate间的间隔时间与振幅，如果没有满足条件的，本次recalculate废除，延续前一次的recalculate或首次计算值

        self.stock_id = stock_id
        self.df_high = pd.read_csv('C:/Users/liquan/Desktop/krama/df_high.csv')
        self.df_close = pd.read_csv('C:/Users/liquan/Desktop/krama/df_close.csv')
        self.df_ave_60 = pd.read_csv('C:/Users/liquan/Desktop/krama/df_ave_60.csv')
        self.df_ave_5 = pd.read_csv('C:/Users/liquan/Desktop/krama/df_ave_5.csv')
        self.df_low = pd.read_csv('C:/Users/liquan/Desktop/krama/df_low.csv')
        self.df_open = pd.read_csv('C:/Users/liquan/Desktop/krama/df_open.csv')
        self.sgjt_high = self.df_high.loc[:, stock_id]
        self.dif = max(self.sgjt_high) - min(self.sgjt_high)
        self.ef = round((36 / 12.5) * self.dif / 196, 4)
        # 近60日的收盘价
        self.close = self.df_close.loc[136:, stock_id]
        self.open = self.df_close.loc[136:, stock_id]
        # 近60日的最低价（10月25号前）
        self.low = self.df_low.loc[136:, stock_id]
        # 近60日的最高价（10月25号前）
        self.high = self.df_high.loc[136:, stock_id]
        # 近60个60日均线价（10月25号前）
        self.ave_60 = self.df_ave_60.loc[:, stock_id]
        # self.stock_data = pd.concat([self.close, self.low, self.high, self.ave_60],axis=1)
        self.stock_data = pd.concat([pd.concat([self.close, self.high, self.low,self.open], 1, ignore_index=True).reset_index(drop=True),
                   pd.DataFrame(self.ave_60).reset_index(drop=True)], 1)
        self.stock_data.columns = ['close', 'high', 'low', 'ave_60']
        obj = Line(stock_id)
        #print obj.order_low
        # peak(a)：波峰收盘价（a1,a2,a3,a4....由近及远）[当日收盘价高于60日均线价的才算波峰]；
        df0,cv0 = obj.pressure_line()
        self.peak = df0.price  # len(peak)>2
        # trough(b)：波谷收盘价（b1,b2,b3,b4....由近及远）[当日收盘价小于60均线价的才算波谷]；
        df1,cv1 = obj.support_line()
        self.trough = df1.price  # len(trough)>2

        obj1 = Angle(stock_id)
        df = obj1.Angle_data(stock_id)
        # 60日均线的角度
        self.angle = obj1.Linemodel(df)  # 45> angle >0
        #print self.stock_data.shape
        # 最近一次波峰收盘价
        self.peak_close = list(self.stock_data.loc[self.stock_data.high == list(self.peak)[-1], 'close'])[-1]
        # 最近一次波谷收盘价
        self.trough_close = list(self.stock_data.loc[self.stock_data.low == list(self.trough)[-1], 'close'])[-1]
        # first_buy_price(c)：标准位价（预计第一次买入价）
        self.first_buy_price = obj.Cross_dot()[-1] * 2 - self.peak_close  # 考虑欠涨的情况为（line.Cross_dot()[-1]+line.Cross_dot(-2）） - peak_close【是否要写个超欠涨的list】
        # first_sell_price(c)：标准位价（预计第一次卖出价）
        self.first_sell_price = obj.Cross_dot()[-1] * 2 - self.trough_close  # 考虑欠涨的情况为（line.Cross_dot()[-1]+line.Cross_dot(-2）） - peak_close【是否要写个超欠涨的list】

        # c_max：最大下标准价位（由a1所得）
        self.c_max = obj.Cross_dot()[-1] * 2 - list(self.peak)[-1]  # 考虑欠涨的情况为（line.Cross_dot()[-1]+line.Cross_dot(-2）） - peak[-1]【是否要写个超欠涨的list】
        # t：60日回归线与日线交点价（t1,t2,t3...由近及远）
        self.t = obj.Cross_dot()
        # close_price：当日收盘价
        self.close_price = list(self.df_close.loc[136:, stock_id])[-1]
        #当日最高价
        self.high_price = list(self.df_high.loc[136:, stock_id])[-1]
        # 当日最低价
        self.low_price = list(self.df_low.loc[136:, stock_id])[-1]
        # ave_60_price(ave_60)：当日60日均线价
        self.ave_60_price = list(self.df_ave_60.loc[:, stock_id])[-1]


        # price_least：当日最低价
        self.price_least = list(self.df_low.loc[136:, stock_id])[-1]
        # price_most:当日最高价
        self.price_most = list(self.df_high.loc[136:,stock_id])[-1]
        # price_least_in3： 三个月内最低价
        self.price_least_in3 = min(list(self.df_low.loc[136:, stock_id]))
        # price_most_in3： 三个月内最高价
        self.price_most_in3 = max(list(self.df_high.loc[136:, stock_id]))
        # price_least_in6： 6个月内最低价
        self.price_least_in6 = min(list(self.df_low.loc[76:, stock_id]))
        # price_most_in6： 6个月内最高价
        self.price_most_in6 = max(list(self.df_high.loc[16:, stock_id]))
        # price_least_in9： 9个月内最低价
        self.price_least_in9 = min(list(self.df_low.loc[16:, stock_id]))
        # price_most_in9： 9个月内最高价
        self.price_most_in9 = max(list(self.df_high.loc[16:, stock_id]))
#################*****************************加数据
        # price_least_in9： 9个月内最低价
        self.price_least_in12 = min(list(self.df_low.loc[16:, stock_id]))
        # price_most_in9： 9个月内最高价
        self.price_most_in12 = max(list(self.df_high.loc[16:, stock_id]))






# code,代码
# name,名称
# industry,所属行业
# area,地区
# pe,市盈率
# outstanding,流通股本(亿)
# totals,总股本(亿)
# totalAssets,总资产(万)
# liquidAssets,流动资产
# fixedAssets,固定资产
# reserved,公积金
# reservedPerShare,每股公积金
# esp,每股收益
# bvps,每股净资
# pb,市净率
# timeToMarket,上市日期
# undp,未分利润
# perundp, 每股未分配
# rev,收入同比(%)
# profit,利润同比(%)
# gpr,毛利率(%)
# npr,净利润率(%)
# holders,股东人数
x = ts.get_stock_basics()
# 每股净资产，每股公积金，每股未分配利润（经验证）
x.loc[x.index=='000006',['bvps','reservedPerShare','perundp']]
