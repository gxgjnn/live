# -*- coding: utf-8 -*-

from STOCK_CHOOSE.stock_box import Calculation
from STOCK_CHOOSE.standard_wave import Wave


class Strategy2(Calculation):
    """
    def selling():situation3-7中，卖出数量不到200的按200算，200为可调参数
    """

    def __init__(self, stock_id):
        super(Calculation, self).__init__(stock_id)

    def selling_buying(self):
        obj0 = Wave(self.stock_id)
        e_pressure_fox, e_support_fox, e_pressure_fox_smaller, e_support_fox_larger, tim, close_time_dis \
            = obj0.standard_wave()
        # 支撑线压力线，波谷波峰数据集，变异系数，支撑点压力点，以及原因的获取
        # df_s, cv_s, price_s = self.support_line()
        e_support, reason_s = self.support_dot()
        # df_p, cv_p, price_p = self.pressure_line()
        e_pressure, reason_p = self.pressure_dot()
        # 超过20这个范围标准计算值会不准，要测试
        buy_price0 = 0
        buy_price1 = 0
        buy_price2 = 0
        sell_price0 = 0
        sell_price1 = 0
        sell_price2 = 0

        if close_time_dis < 20:

            # 在压力位内侧的时候
            if (e_pressure_fox <= e_pressure) and (e_pressure_fox != 0):
                # 若存在最近标准位为压力
                if e_pressure_fox_smaller != 0:
                    # 最近标准位高于当日最高价
                    # if e_pressure_fox_smaller >= self.df.high[0]:
                        # 最近标准位大于标准位
                        if e_pressure_fox_smaller >= e_pressure_fox:
                            # 最近标准位和标准位都没超过压力位
                            if e_pressure_fox_smaller <= e_pressure:
                                if (e_pressure_fox / self.ave_price_60[0]) > 1.05:
                                    # 之前已经平衡，那么从最新波点算起
                                    sell_price0 = e_pressure_fox_smaller
                                    sell_price1 = e_pressure
                                    print 'standard_wave situation1'
                                else:
                                    if (e_pressure_fox_smaller / self.ave_price_60[0]) > 1.05:
                                        sell_price0 = e_pressure_fox_smaller
                                        sell_price1 = e_pressure
                                        print 'standard_wave situation2'
                                    else:
                                        # 如果e_pressure依旧离60日均线5%以内，也按照e_pressure卖出
                                        sell_price0 = e_pressure
                                        sell_price1 = 0
                                        print 'standard_wave situation3'
                            else:
                                # 之前已经平衡，那么从最新波点算起，e_pressure_fox忽略
                                if (e_pressure / self.ave_price_60[0]) > 1.05:
                                    sell_price0 = e_pressure
                                    sell_price1 = e_pressure_fox_smaller
                                    print 'standard_wave situation4'
                                else:
                                    sell_price0 = e_pressure_fox_smaller
                                    sell_price1 = 0
                                    print 'standard_wave situation5'
                        # 最近标准位小于标准位
                        else:
                            if e_pressure_fox <= e_pressure:
                                if (e_pressure_fox_smaller / self.ave_price_60[0]) > 1.05:
                                    sell_price0 = e_pressure_fox_smaller
                                    sell_price1 = e_pressure_fox
                                    sell_price2 = e_pressure
                                    print 'standard_wave situation6'
                                else:
                                    if (e_pressure_fox / self.ave_price_60[0]) > 1.05:
                                        sell_price0 = e_pressure_fox
                                        sell_price1 = e_pressure
                                        print 'standard_wave situation7'
                                    else:
                                        sell_price0 = e_pressure
                                        sell_price1 = 0
                                        print 'standard_wave situation8'
                            else:
                                if (e_pressure_fox_smaller / self.ave_price_60[0]) > 1.05:
                                    sell_price0 = e_pressure_fox_smaller
                                    sell_price1 = e_pressure
                                    sell_price2 = e_pressure_fox
                                    print 'standard_wave situation9'
                                else:
                                    if (e_pressure / self.ave_price_60[0]) > 1.05:
                                        sell_price0 = e_pressure
                                        sell_price1 = e_pressure_fox
                                        print 'standard_wave situation10'
                                    else:
                                        sell_price0 = e_pressure_fox
                                        sell_price1 = 0
                                        print 'standard_wave situation11'

                elif e_support_fox_larger != 0:
                    if e_support_fox_larger < e_support:
                        if (e_support / self.ave_price_60[0]) <= 0.95:
                            buy_price0 = e_support
                            buy_price1 = e_support_fox_larger
                            print 'standard_wave situation12'
                        else:
                            if (e_support_fox_larger / self.ave_price_60[0]) <= 0.95:
                                buy_price0 = e_support_fox_larger
                                # 没有else，没有参数满足买入条件
                                print 'standard_wave situation13'
                    else:
                        if (e_support_fox_larger / self.ave_price_60[0]) <= 0.95:
                            buy_price0 = e_support_fox_larger
                            buy_price1 = e_support
                            print 'standard_wave situation14'
                        else:
                            buy_price0 = e_support
                            # 没有else，没有参数满足买入条件
                            print 'standard_wave situation15'
#########################################################################
            # 在压力位外侧的时候
            elif (e_pressure_fox > e_pressure) and (e_pressure_fox != 0):
                # 若存在最近标准位为压力
                if e_pressure_fox_smaller != 0:
                    if e_pressure_fox_smaller >= e_pressure:
                        # 最近标准位和标准位都没超过压力位
                        if e_pressure_fox_smaller <= e_pressure_fox:
                            if (e_pressure / self.ave_price_60[0]) > 1.05:
                                sell_price0 = e_pressure
                                sell_price1 = e_pressure_fox_smaller
                                sell_price2 = e_pressure_fox
                                print 'standard_wave situation16'
                            else:
                                if (e_pressure_fox_smaller / self.ave_price_60[0]) > 1.05:
                                    sell_price0 = e_pressure_fox_smaller
                                    sell_price1 = e_pressure_fox
                                    print 'standard_wave situation17'
                                # else的情况理应不存在，因为太小
                                else:
                                    sell_price0 = e_pressure_fox
                                    sell_price1 = 0
                                    print 'standard_wave situation18'
                        # 最近标准位超过压力位，但标准位没有超过压力位，要么标准位太小，要么最近标准位走势太猛，尴尬
                        else:
                            if (e_pressure / self.ave_price_60[0]) > 1.05:
                                sell_price0 = e_pressure
                                sell_price1 = e_pressure_fox
                                sell_price2 = e_pressure_fox_smaller
                                print 'standard_wave situation19'
                            else:
                                if (e_pressure_fox / self.ave_price_60[0]) > 1.05:
                                    sell_price0 = e_pressure_fox
                                    sell_price1 = e_pressure_fox_smaller
                                    print 'standard_wave situation20'
                                # else的情况理应不存在，因为太小
                                else:
                                    sell_price0 = e_pressure_fox_smaller
                                    sell_price1 = 0
                                    print 'standard_wave situation21'
                    # 最近标准位小于标准位
                    else:
                        if (e_pressure_fox_smaller / self.ave_price_60[0]) > 1.05:
                            sell_price0 = e_pressure_fox_smaller
                            sell_price1 = e_pressure
                            sell_price2 = e_pressure_fox
                            print 'standard_wave situation22'
                        else:
                            if (e_pressure / self.ave_price_60[0]) > 1.05:
                                sell_price0 = e_pressure
                                sell_price1 = e_pressure_fox
                                print 'standard_wave situation23'
                            else:
                                # 不管e_pressure_fox距离60日均线多近，除了更改1.05的参数之外，可以忽略1.05
                                sell_price0 = e_pressure_fox
                                print 'standard_wave situation24'

                # 和压力位内测的e_support_fox_larger != 0的情况一样
                elif e_support_fox_larger != 0:
                    if e_support_fox_larger < e_support:
                        if (e_support / self.ave_price_60[0]) <= 0.95:
                            buy_price0 = e_support
                            buy_price1 = e_support_fox_larger
                            print 'standard_wave situation25'
                        else:
                            if (e_support_fox_larger / self.ave_price_60[0]) <= 0.95:
                                buy_price0 = e_support_fox_larger
                                # 没有else，没有参数满足买入条件
                                print 'standard_wave situation26'
                    else:
                        if (e_support_fox_larger / self.ave_price_60[0]) <= 0.95:
                            buy_price0 = e_support_fox_larger
                            buy_price1 = e_support
                            print 'standard_wave situation27'
                        else:
                            buy_price0 = e_support
                            # 没有else，没有参数满足买入条件
                            print 'standard_wave situation28'
#############################################################################
            # 在支撑位内侧的时候
            elif (e_support <= e_support_fox) and (e_support_fox != 0):
                # 若存在最近标准位为压力
                if e_pressure_fox_smaller != 0:
                    # 最近标准位和标准位都没超过压力位
                    if e_pressure_fox_smaller > e_pressure:
                        if (e_pressure / self.ave_price_60[0]) > 1.05:
                            sell_price0 = e_pressure
                            sell_price1 = e_pressure_fox_smaller
                            print 'standard_wave situation29'
                        else:
                            if (e_pressure_fox_smaller / self.ave_price_60[0]) >= 1.05:
                                sell_price0 = e_pressure_fox_smaller
                                print 'standard_wave situation30'
                    else:
                        if (e_pressure_fox_smaller / self.ave_price_60[0]) >= 1.05:
                            sell_price0 = e_pressure_fox_smaller
                            sell_price1 = e_pressure
                            print 'standard_wave situation31'
                        else:
                            if (e_pressure / self.ave_price_60[0]) >= 1.05:
                                sell_price0 = e_pressure
                                # 没有else，没有参数满足买入条件，宁可等到新的波谷出现
                                print 'standard_wave situation32'

                elif e_support_fox_larger != 0:
                    # 在e_support_fox下侧
                    if e_support_fox_larger <= e_support_fox:
                        # 在e_support上侧
                        if e_support_fox_larger >= e_support:
                            if (e_support_fox / self.ave_price_60[0]) < 0.95:
                                buy_price0 = e_support_fox
                                buy_price1 = e_support_fox_larger
                                buy_price2 = e_support
                                print 'standard_wave situation33'
                            else:
                                if (e_support_fox_larger / self.ave_price_60[0]) < 0.95:
                                    buy_price0 = e_support_fox_larger
                                    # 第二次买入没有成功的时候，如果新波谷确认，记得要从waiting_box里删除
                                    buy_price1 = e_support
                                    print 'standard_wave situation34'
                                # else的情况理应不存在，因为太小
                                else:
                                    buy_price0 = e_support
                                    # else不存在，没有参数满足买入条件
                                    print 'standard_wave situation35'
                        else:
                            if (e_support_fox / self.ave_price_60[0]) < 0.95:
                                buy_price0 = e_support_fox
                                buy_price1 = e_support
                                buy_price2 = e_support_fox_larger
                                print 'standard_wave situation36'
                            else:
                                if (e_support / self.ave_price_60[0]) < 0.95:
                                    buy_price0 = e_support
                                    # 第二次买入没有成功的时候，如果新波谷确认，记得要从waiting_box里删除
                                    buy_price1 = e_support_fox_larger
                                    print 'standard_wave situation37'
                                # else的情况理应不存在，因为太小
                                else:
                                    buy_price0 = e_support
                                    print 'standard_wave situation38'
                    # 最近标准位小于标准位
                    else:
                        if (e_support_fox_larger / self.ave_price_60[0]) < 0.95:
                            buy_price0 = e_support_fox_larger
                            buy_price1 = e_support_fox
                            buy_price2 = e_support
                            print 'standard_wave situation39'
                        else:
                            if (e_support_fox / self.ave_price_60[0]) < 0.95:
                                buy_price0 = e_support_fox
                                # 第二次买入没有成功的时候，如果新波谷确认，记得要从waiting_box里删除
                                buy_price1 = e_support
                                print 'standard_wave situation40'
                            else:
                                buy_price0 = e_support
                                print 'standard_wave situation41'
##############################################################################
            # 在支撑位外侧的时候
            elif (e_support > e_support_fox) and (e_support_fox != 0):
                # 同支撑位内测的时候一样
                if e_pressure_fox_smaller != 0:
                    # 最近标准位和标准位都没超过压力位
                    if e_pressure_fox_smaller > e_pressure:
                        if (e_pressure / self.ave_price_60[0]) > 1.05:
                            sell_price0 = e_pressure
                            sell_price1 = e_pressure_fox_smaller
                            print 'standard_wave situation42'
                        else:
                            if (e_pressure_fox_smaller / self.ave_price_60[0]) >= 1.05:
                                sell_price0 = e_pressure_fox_smaller
                                print 'standard_wave situation43'
                    else:
                        if (e_pressure_fox_smaller / self.ave_price_60[0]) >= 1.05:
                            sell_price0 = e_pressure_fox_smaller
                            sell_price1 = e_pressure
                            print 'standard_wave situation44'
                        else:
                            if (e_pressure / self.ave_price_60[0]) >= 1.05:
                                sell_price0 = e_pressure
                                # 没有else，没有参数满足买入条件，宁可等到新的波谷出现
                                print 'standard_wave situation45'

                elif e_support_fox_larger != 0:
                    # 在e_support下侧
                    if e_support_fox_larger <= e_support:
                        # 在e_support_fox上侧
                        if e_support_fox_larger >= e_support_fox:
                            if (e_support / self.ave_price_60[0]) < 0.95:
                                buy_price0 = e_support
                                buy_price1 = e_support_fox_larger
                                buy_price2 = e_support_fox
                                print 'standard_wave situation46'
                            else:
                                if (e_support_fox_larger / self.ave_price_60[0]) < 0.95:
                                    buy_price0 = e_support_fox_larger
                                    # 第二次买入没有成功的时候，如果新波谷确认，记得要从waiting_box里删除
                                    buy_price1 = e_support_fox
                                    print 'standard_wave situation47'
                                # else的情况理应不存在，因为太少
                                else:
                                    if (e_support / self.ave_price_60[0]) < 0.95:
                                        buy_price0 = e_support_fox
                                        # 不存在else没有满足买入条件的参数
                                        print 'standard_wave situation48'
                        else:
                            if (e_support / self.ave_price_60[0]) < 0.95:
                                buy_price0 = e_support
                                buy_price1 = e_support_fox
                                buy_price2 = e_support_fox_larger
                                print 'standard_wave situation49'
                            else:
                                if (e_support_fox / self.ave_price_60[0]) < 0.95:
                                    buy_price0 = e_support_fox
                                    # 第二次买入没有成功的时候，如果新波谷确认，记得要从waiting_box里删除
                                    buy_price1 = e_support_fox_larger
                                    print 'standard_wave situation50'
                                else:
                                    if (e_support_fox_larger / self.ave_price_60[0]) < 0.95:
                                        buy_price0 = e_support_fox_larger
                                        # 不存在else没有满足买入条件的参数
                                        print 'standard_wave situation51'
                    # 最近标准位小于标准位
                    else:
                        if (e_support_fox_larger / self.ave_price_60[0]) < 0.95:
                            buy_price0 = e_support_fox_larger
                            buy_price1 = e_support
                            buy_price2 = e_support_fox
                            print 'standard_wave situation52'
                        else:
                            if (e_support / self.ave_price_60[0]) < 0.95:
                                buy_price0 = e_support
                                # 第二次买入没有成功的时候，如果新波谷确认，记得要从waiting_box里删除
                                buy_price1 = e_support_fox
                                print 'standard_wave situation53'
                            else:
                                if (e_support_fox / self.ave_price_60[0]) < 0.95:
                                    buy_price0 = e_support_fox
                                    print 'standard_wave situation54'
##############################################
        # 只靠压力/支撑位，最近标准位计算
        else:
            print '距今间隔', close_time_dis

            if e_support_fox_larger != 0:
                if e_support_fox_larger >= e_support:
                    if (e_support_fox_larger / self.ave_price_60[0]) < 0.95:
                        buy_price0 = e_support_fox_larger
                        buy_price1 = e_support
                        print 'standard_wave situation55'
                    else:
                        buy_price0 = e_support
                        print 'standard_wave situation56'
                else:
                    # 区别在于30个交易日以内有e_support_fox作为主要买卖标准，而30个交易日以外的以e_support为主要交易标准
                    buy_price0 = e_support
                    buy_price1 = e_support_fox_larger
                    print 'standard_wave situation57'

            elif e_pressure_fox_smaller != 0:
                if e_pressure_fox_smaller <= e_pressure:
                    if (e_pressure_fox_smaller / self.ave_price_60[0]) >= 1.05:
                        sell_price0 = e_pressure_fox_smaller
                        sell_price1 = e_pressure
                        print 'standard_wave situation58'
                    else:
                        sell_price0 = e_pressure
                        print 'standard_wave situation59'
                else:
                    sell_price0 = e_pressure
                    sell_price1 = e_pressure_fox_smaller
                    print 'standard_wave situation60'

        return buy_price0, buy_price1, buy_price2, sell_price0, sell_price1, sell_price2


if __name__ == "__main__":
    pass