# -*- coding: utf-8 -*-

from STOCK_CHOOSE.standard_wave import Wave
import pandas as pd
import math


class Initial(Wave):

    def __init__(self, stock_id, num_buy, num_sell):
        """
        
        :param stock_id: 
        :param num_buy: online系统可用资金计算出来的个股可买数量
        :param num_sell: online系统个股持股数量
        """
        #  super(Wave, self).__init__(stock_id)
        Wave.__init__(self, stock_id)
        self.num_buy = num_buy
        self.num_sell = num_sell

    def num_buy_process(self, coe, data):
        """
        
        :param coe: 买入系数
        :param data: low_data---- low_offer = [self.price_s, e_support_fox, e_support_fox_larger],去0后的low_2
        :return: 
        """
        if self.num_buy > 300:
            num_buy0 = self.num_buy * coe / len(data)
            num_buy1 = math.floor(num_buy0 / 100) * 100
            if num_buy1 <= 100:
                num_buy1 = 100
        else:
            num_buy1 = self.num_buy
            print 'available amount negative'
        return num_buy1

    def num_sell_process(self, coe):
        # 卖出下取整，20%的数量处理
        if self.num_sell > 300:
            num_sell0 = self.num_sell / coe
            num_sell1 = math.floor(num_sell0 / 100) * 100
            if num_sell1 == 0:
                num_sell1 = 100
        else:
            num_sell1 = self.num_sell
            print 'sell all out'
        return num_sell1

    def quoting(self):
        """
        # 从stock_box里的股票经standard_wave过滤后的股票
        # 从模拟持仓系统获取的股票（从该通道进来的股票要监控，发现变形要及时止损）
        :return: df_sell, df_buy两个DataFrame({'price':,'num':}) ，包含止损价不包含0
        """
        e_pressure_fox, e_support_fox, e_pressure_fox_smaller, e_support_fox_larger, current_dis, close_time_dis, fox \
            = self.standard_wave()
        df_sell = pd.DataFrame([])
        df_buy = pd.DataFrame([])
        # 在class Line里限制了e_support(self.ave_price_60[0] > predict_price)而没有限制e_pressure
        if self.price_p > self.ave_price_60[0]:
            up_offer = [self.price_p, e_pressure_fox, e_pressure_fox_smaller]
            low_offer = [self.price_s, e_support_fox, e_support_fox_larger]
            # 限制距离,与当日60日均线价以上5%为界限分类
            # if (up_min / self.ave_price_60[0] >= 1.05) and (low_est / self.ave_price_60[0] <= 0.95):
            # 报价纠正,给破位或者计算失准的股票一次机会
            up_2 = [self.price_p, e_pressure_fox, e_pressure_fox_smaller]
            for i in up_offer:
                if i == 0:
                    up_2.remove(0)
            # 去重
            up_2 = list(set(up_2))
            low_2 = [self.price_s, e_support_fox, e_support_fox_larger]
            for i in low_offer:
                if i == 0:
                    low_2.remove(0)
            # 去重
            low_2 = list(set(low_2))
            # 去0后的list
            low_min_ren = min(low_2)
            index_0 = low_offer.index(low_min_ren)
            # yang = 0
            # yin = 0
            if low_min_ren > self.df.high[0]:
                # 考虑到改变最低价的最大百分比是向下1%，会导致止损价多下降1%，所以不能太大
                if (low_min_ren / self.df.high[0]) < 1.01:
                    low_offer[index_0] = self.ave_price_5[0]
                    # for i in range(8):
                    #     if self.df.open[i] - self.df.close[i] >= 0:
                    #         yang += 1
                    #     else:
                    #         yin += 1
                    # # 计算箱体和阴阳比例
                    # data = self.angle_data(ave=5, stop_dot=8)
                    # angle, a, b, model = self.line_model(data)
                    # if (yang > yin) and (-15 <= angle <= 15):
                    #     # 赋5日均线值
                    #     low_offer[index_0] = self.ave_price_5[0]
                    # else:
                    #     low_offer = [0, 0, 0]
                else:
                    low_offer = [0, 0, 0]

            # num权重分配
            # 卖出下取整，20%的数量处理
            num_sell1 = self.num_sell_process(coe=5)
            # 卖出10%的情况数量处理
            num_sell3 = self.num_sell_process(coe=10)
            # 卖出50%的情况数量处理
            num_sell2 = self.num_sell_process(coe=2)

            # 买入下取整，考虑到每股可用资金尽量放小，而增加数量测试的目的，只用300，和100
            num_buy1 = self.num_buy_process(coe=0.333, data=low_2)
            num_buy3 = self.num_buy_process(coe=0.533, data=low_2)
            num_buy5 = self.num_buy_process(coe=0.133, data=low_2)
            num_buy7 = self.num_buy_process(coe=0.433, data=low_2)
            num_buy9 = self.num_buy_process(coe=0.067, data=low_2)
            num_buy11 = self.num_buy_process(coe=0.6, data=low_2)
            num_buy13 = self.num_buy_process(coe=0.467, data=low_2)

            # 以下sell_num,buy_num列表内会有0的情况
            sell_num = [num_sell1, num_sell1, num_sell1]
            buy_num = [num_buy1, num_buy1, num_buy1]
            # up_offer = [self.price_p, e_pressure_fox, e_pressure_fox_smaller]
            # low_offer = [self.price_s, e_support_fox, e_support_fox_larger]
            if current_dis < 60:
                # fox是否为空，只考虑buy的权重分配
                if fox.empty:
                    # 分割系数
                    if e_support_fox_larger == 0:
                        buy_num = [num_buy3, num_buy5, num_buy1]
                    else:
                        buy_num = [num_buy7, num_buy5, num_buy7]
            else:
                sell_num = [num_sell1, num_sell3, num_sell1]
                if fox.empty:
                    if e_support_fox_larger == 0:
                        buy_num = [num_buy11, num_buy9, num_buy1]
                    else:
                        buy_num = [num_buy13, num_buy9, num_buy13]

            # 加入止损价格和数量
            if len(low_2) == 1:
                stop_price = min(low_2) * 0.97
                up_offer.extend([stop_price])
                sell_num.extend([self.num_sell])
            elif len(low_2) == 2:
                stop_price = max(low_2) * 0.97
                up_offer.extend([stop_price])
                sell_num.extend([num_sell2])

                stop_price = min(low_2) * 0.97
                up_offer.extend([stop_price])
                sell_num.extend([self.num_sell])
            else:
                stop_price = max(low_2) * 0.97
                up_offer.extend([stop_price])
                sell_num.extend([num_sell2])

                no2 = min(set(low_2) - set([max(low_2)]))
                stop_price = no2 * 0.97
                up_offer.extend([stop_price])
                sell_num.extend([num_sell2])

                stop_price = min(low_2) * 0.97
                up_offer.extend([stop_price])
                sell_num.extend([self.num_sell])
            # 生成除0数据框，未对price排序
            df_buy = pd.DataFrame({'price_buy': low_offer, 'buy_num': buy_num})
            df_sell = pd.DataFrame({'price_sell': up_offer, 'sell_num': sell_num})
            df_buy = df_buy.loc[df_buy.price_buy != 0, ]
            df_sell = df_sell.loc[df_sell.price_sell != 0, ]
            # 去重
            df_buy.drop_duplicates(inplace=True)
            df_sell.drop_duplicates(inplace=True)
            # 去除没有持股数的情况
            df_sell = df_sell.loc[df_sell.sell_num != 0, ]
            return df_sell, df_buy

        else:
            print '！！！压力线下穿60日均线，赶紧来打补丁！！！'

        return df_sell, df_buy


if __name__ == "__main__":
    stock = '000989'
    num_selling = 0
    num_buying = 1100
    obj = Initial(stock, num_buy=num_buying, num_sell=num_selling)
    s, b = obj.quoting()
    print '挂卖单:\n', s
    print '挂买单:\n', b