# -*- coding: utf-8 -*-

from STOCK_CHOOSE.stock_box_back import Calculation_back
from DEAL.strategy2_initial_back import Initial
from utils.newdata_achieve import *
from SIMULATION.deal_windows_back import *
from DEAL.deal import Deal
from DEAL.info_online import *
import string
import logging
logging.basicConfig()


class Box(Account):
    # def __init__(self, date_back):
    #     self.date_back = date_back
    #     super(Account, self).__init__(engine)
    #     self.engine = engine
    def create_box(self, date_star):
        """
        # 选股,犹豫要不要存，最后选择存
        :return: list of chosen stocks
        """
        start = datetime.datetime.now()
        stock_box = []
        stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                       dtype={'code': np.str})
        codes = stock_basic_list.code
        for stock in codes:
            obj_5 = Calculation_back(stock, stock_box, date_star)
            obj_5.stocks_choose()
            print 'stock', stock
            print 'stock_box', stock_box
            print '*' * 30
        # stock_box = ['600459', '000989']
        stock_box = str(stock_box)
        # tik = time.strftime("%Y-%m-%d", time.localtime())
        tik = date_star
        stocks_chosen_daily = pd.DataFrame([[tik, stock_box]], columns=['date', 'stocks_chosen_daily'])
        stocks_chosen_daily.to_sql(con=self.engine, name="stocks_chosen_daily_50_new", if_exists='append', index=False)
        print 'first', stock_box

        end = datetime.datetime.now()
        secondsDiff = (end - start).seconds
        minutesDiff = round(secondsDiff / 60, 1)
        print 'create_box_minutesDiff', minutesDiff

    def store_bad_package(self, data):
        tik = date_star
        stocks_chosen_daily = pd.DataFrame([[tik, data]], columns=['date', 'bad_package'])
        stocks_chosen_daily.to_sql(con=self.engine, name="bad_package", if_exists='replace', index=False)


# 次日9:15am
# 1、从模拟窗口循环获取num_selling,num_buying
def stocks_order(box, bad_package):
    """
    # 每个交易日首次委托，要更新当日委托表，历史委托表，账户表
    :param box: return from def create_box()
    :return: 
    """
    start = datetime.datetime.now()
    obj_0 = Current()
    obj_1 = History()
    obj_2 = Account()
    obj_3 = Deal()
    obj_5 = Box()
    holding_stock_detail = data_process.get_holding_stock_detail_current_back()
    bad_package_yesterday = data_process.get_bad_package_yesterday_back()
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    bad = str(np.array(bad_package_yesterday.iloc[0, 1]))
    bad = bad.translate(None, string.punctuation).split()
    new_box = set(box) - set(bad) - set(bad_package)
    # 存今天的bad_package
    obj_5.store_bad_package(data=str(bad_package))

    order_id = 1
    for stock in new_box:
        # 回测用作可买股数的依据，用前一工作日收盘价
        date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
        # 数据类型转换
        date_star1 = date_star0
        date_star_end = date_star1.strftime('%Y-%m-%d')
        # 数据类型转换，用了-8，考虑国内最长假期为7天
        date_star2 = date_star0 + datetime.timedelta(-8)
        date_star_start = date_star2.strftime('%Y-%m-%d')
        # t_s = ts.get_h_data(stock, start=date_star_start, end=date_star_end, autype='qfq', drop_factor=False)
        error, t_s = get_h_data(stock, date_star_start, date_star_end)
        while error != 0:
            time.sleep(100)
            error, t_s = get_h_data(stock, date_star_start, date_star_end)
        if t_s.empty:
            continue
        price = float(t_s.iloc[0, 2])
        num_sell, available_money = trade_data(stock)
        num_buy = num_transfer(available_money, num_sell, price)
        if num_buy < 0:
            print 'num_buy 小于0'
            continue
        obj_4 = Initial(stock, num_buy=num_buy, num_sell=num_sell, date=date_star)
        order_sell, order_buy = obj_4.quoting()
        # 挂单操作
        if order_buy.empty:
            print stock, '选股订单买入委托为空，原因为报价大于实价后的报价纠正,现最高价已破支撑位'
            continue
        # 挂买单跟新昨天委托表
        print 'stock_id:', stock
        for i in range(len(order_buy)):
            date = date_star
            order_time = time.strftime("%H:%M:%S", time.localtime())
            # stock_name = list(stock_basic_list.loc[stock_basic_list.code == stock, 'name'])[0]
            stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[0]
            order_status = 'buy'
            order_price = round(np.array(order_buy.price_buy)[i], 2)
            order_num = np.array(order_buy.buy_num)[i]
            # 委托买入时，除了正常股价还有服务费要锁定
            commission_buy, commission_sell = obj_3.order_cost(order_num, order_price, close_tax=0.001,
                                                               open_commission=0.0003,
                                                               close_commission=0.0003, min_commission=5)
            lock_amount = round((order_num * order_price + commission_buy), 2)
            deal_amount = 0
            deal_num = 0
            deal_status = 'undeal'
            # 委托下单,当日委托表更新
            obj_0.current_place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                                      lock_amount,
                                      deal_amount, deal_num, order_time, deal_status)
            # 历史委托表更新
            obj_1.place_order(date, order_id, stock, stock_name, order_status, order_price, order_num, lock_amount,
                              deal_amount, deal_num, order_time, deal_status)
        time.sleep(10)
    # 读库
    order_stock_detail = data_process.get_order_stock_detail_current_back()
    # 帐户表Account更新
    obj_2.account_detail(order_id, holding_stock_detail, order_stock_detail, date_star)

    ware = holding_stock_detail.iloc[:, 1]
    new_ware = set(ware.values)-set(bad_package)
    for stock in new_ware:
        print 'stock_id', stock
        # 填补缺0值
        stock = str(stock).zfill(6)
        # 回测用作可买股数的依据，用前一工作日收盘价
        date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
        # 数据类型转换
        date_star1 = date_star0
        date_star_end = date_star1.strftime('%Y-%m-%d')
        # 数据类型转换，用了-8，考虑国内最长假期为7天
        date_star2 = date_star0 + datetime.timedelta(-8)
        date_star_start = date_star2.strftime('%Y-%m-%d')
        # t_s = ts.get_h_data(stock, start=date_star_start, end=date_star_end, autype='qfq', drop_factor=False)
        error, t_s = get_h_data(stock, date_star_start, date_star_end)
        while error != 0:
            time.sleep(100)
            error, t_s = get_h_data(stock, date_star_start, date_star_end)
        if t_s.empty:
            continue
        price = float(t_s.iloc[0, 2])
        num_sell, available_money = trade_data_back(stock)
        num_buy = num_transfer(available_money, num_sell, price)
        obj_4 = Initial(stock, num_buy=num_buy, num_sell=num_sell, date=date_star)
        order_sell, order_buy = obj_4.quoting()
        # 挂单操作
        if order_sell.empty:
            print stock, '持仓卖单委托为空，可卖股数为0'
            continue
        # 挂卖单append到今日委托表
        for i in range(len(order_sell)):
            date = date_star
            order_time = time.strftime("%H:%M:%S", time.localtime())
            stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[0]
            order_status = 'sell'
            order_price = round((np.array(order_sell.price_sell)[i]), 2)
            order_num = np.array(order_sell.sell_num)[i]
            # 委托卖出时，除了正常股价还有服务费要锁定
            commission_buy, commission_sell = obj_3.order_cost(order_num, order_price, close_tax=0.001,
                                                               open_commission=0.0003,
                                                               close_commission=0.0003, min_commission=5)
            # 从变现的股票中扣除手续费
            lock_amount = round((order_num * order_price - commission_sell), 2)
            deal_amount = 0
            deal_num = 0
            deal_status = 'undeal'
            # 委托下单,当日委托表更新
            obj_0.current_place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                                      lock_amount,
                                      deal_amount, deal_num, order_time, deal_status)
            # 历史委托表更新
            obj_1.place_order(date, order_id, stock, stock_name, order_status, order_price, order_num, lock_amount,
                              deal_amount, deal_num, order_time, deal_status)
        time.sleep(10)
        # 卖出委托不需要更新帐户表；因为卖出百分比定死，这里不改变持仓表可用持仓的数值

    end = datetime.datetime.now()
    secondsDiff = (end - start).seconds
    # minutesDiff = round(secondsDiff / 60, 1)
    print 'first_order_secondsDiff', secondsDiff


def get_h_data(stock_id, start, end):
    e = 0
    try:
        t_s = ts.get_h_data(stock_id, start=start, end=end, autype=None, drop_factor=False)
    except Exception, e:
        t_s = pd.DataFrame()
        pass
    return e, t_s


def deal_check2():
    start = datetime.datetime.now()
    obj_0 = Current()
    obj_1 = History()
    obj_2 = Account()
    obj_3 = Deal()
    # 读当日委托表和数据更新表
    order_stock_detail = data_process.get_order_stock_detail_current_back()
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    order_stock_detail = order_stock_detail.loc[order_stock_detail.iloc[:, -1] != 'deal', ]
    # order_stock_detail = order_stock_detail.iloc[41:-33, ]
    # 挂单价 与 更新价比较
    for i in range(len(order_stock_detail.iloc[:, 2])):
        # 必须放在内层，否则股数不会更新
        current_holding_detail = data_process.get_holding_without_0_back()
        stock_id = order_stock_detail.iloc[i, 2]
        order_price = order_stock_detail.iloc[i, 5]
        order_num = order_stock_detail.iloc[i, 6]
        stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock_id, 'name']).split('    ')[1].split('\n')[0]
        # 回测用作下一个交易日是否交易成功的依据，用下一工作日的最高与最低价
        date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
        # 数据类型转换
        date_star1 = date_star0 + datetime.timedelta(1)
        date_star_start = date_star1.strftime('%Y-%m-%d')
        # 数据类型转换，用了-8，考虑国内最长假期为7天
        date_star2 = date_star0 + datetime.timedelta(8)
        date_star_end = date_star2.strftime('%Y-%m-%d')
        # t_s = ts.get_h_data(stock_id, start=date_star_start, end=date_star_end, autype='qfq', drop_factor=False)
        error, t_s = get_h_data(stock_id, date_star_start, date_star_end)
        while error != 0:
            time.sleep(100)
            error, t_s = get_h_data(stock_id, date_star_start, date_star_end)
        if t_s.empty:
            continue
        update_open = float(t_s.iloc[-1, 0])
        update_high = float(t_s.iloc[-1, 1])
        update_low = float(t_s.iloc[-1, 3])
        order_price_new = float(order_price)
        date = date_star
        order_time = time.strftime("%H:%M:%S", time.localtime())
        if update_low <= order_price:
            if order_price > update_open:
                # 拿开盘价替代
                order_price_new = update_open
            # 如果委托状态是'buy'
            if order_stock_detail.iloc[i, 4] == 'buy':
                # date = date_star
                # order_time = time.strftime("%H:%M:%S", time.localtime())
                hold_status = 'buy'
                # 如果是已持有的股票
                if stock_id in np.array(current_holding_detail.iloc[:, 1]):
                    # [[date, stock_id, stock_name, hold_status, origin_price, total_num, origin_amount,
                    #   current_amount, yesterday_num, nowadays_num, available_num, holding_profit, deal_profit]],
                    # columns = ['交易日', '证券代码', '证券名称', '持仓方向', '持仓成本价', '总持仓股数',
                    # '持仓成本金额', '当前总持仓金额', '昨日持仓', '今日持仓', '可用持仓', '持仓盈亏', '交易盈亏']
                    # 加法
                    origin = current_holding_detail.loc[current_holding_detail.iloc[:, 1] == stock_id, :]
                    total_num = origin.iloc[0, 5] + order_num
                    # 持仓成本金额
                    origin_amount = origin.iloc[0, 6] + order_num * order_price_new
                    # 当前总持仓金额,回测拿的是下一个交易日的收盘价做实时价格
                    vs_price = round((t_s.iloc[-1, 2]), 2)
                    current_amount = total_num * vs_price
                    # 持仓成本价
                    origin_price = round((origin_amount / total_num), 2)
                    yesterday_num = origin.iloc[0, 8]
                    nowadays_num = total_num
                    available_num = origin.iloc[0, -3]
                    # 持仓盈亏
                    holding_profit = int(current_amount - origin_amount)
                    # 交易盈亏
                    deal_profit = origin.iloc[0, -1]
                    # 调用当日持仓函数
                    # 限制每个股票的持仓成本金额
                    # if order_price_new <= 20000
                    if origin.iloc[0, 6] <= 20000:
                        obj_0.current_holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                                     origin_amount,
                                                     current_amount, yesterday_num, nowadays_num, available_num,
                                                     holding_profit, deal_profit)
                    else:
                        print stock_id, 'surpass 20000'
                        continue
                    # [[date, order_id, stock_id, stock_name, order_status, order_price, order_num, lock_amount,
                    #   deal_amount, deal_num, order_time, deal_status]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '委托行为', '委托价格',
                    #            '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
                    origin = order_stock_detail.loc[order_stock_detail.iloc[0:, 2] == stock_id, :]
                    origin1 = origin.loc[origin.iloc[0:, 5] == order_price, :]
                    order_id = origin1.iloc[0, 1]
                    order_status = origin1.iloc[0, 4]
                    # 委托卖出时，除了正常股价还有服务费要锁定
                    # commission_buy, commission_sell = obj_3.order_cost(order_num, order_price, close_tax=0.001,
                    #                                                    open_commission=0.0003,
                    #                                                    close_commission=0.0003, min_commission=5)
                    # lock_amount = order_price_new * order_num + commission_buy
                    lock_amount = origin1.iloc[0, 7]
                    # change below 3
                    deal_amount = order_price_new
                    deal_num = order_num
                    deal_status = 'deal'
                    # 调当日委托函数，变化交易状态，只改一条数据
                    obj_0.current_place_order(date, order_id, stock_id, stock_name, order_status, order_price,
                                              order_num, lock_amount,
                                              deal_amount, deal_num, order_time, deal_status)

                    # 委托买入时，除了正常股价还有服务费要锁定
                    commission_buy, commission_sell = obj_3.order_cost(deal_num, order_price_new, close_tax=0.001,
                                                                       open_commission=0.0003,
                                                                       close_commission=0.0003, min_commission=5)
                    # 原锁定金额减去成交费率和成交总金额的和
                    lock_amount_undeal = round((lock_amount - (order_price_new * deal_num + commission_buy)), 2)
                    if lock_amount_undeal != 0:
                        deal_amount_undeal = 0
                        deal_num_undeal = 0
                        # 部分未成交但锁定的金额
                        deal_status = 'undeal'
                        obj_0.current_place_order(date, order_id, stock_id, stock_name, order_status, order_price,
                                                  order_num, lock_amount_undeal,
                                                  deal_amount_undeal, deal_num_undeal, order_time, deal_status)

                    # [[date, order_id, stock_id, stock_name, deal_status, deal_price, deal_num,
                    #   deal_time]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '交易行为', '成交价格',
                    #            '成交数量', '成交时间'])
                    deal_price = order_price_new
                    deal_time = order_time
                    status = 'buy'
                    # 调用当日成交函数
                    obj_0.current_deal_detail(date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                              deal_time)
                    # 调用历史成交函数
                    obj_1.deal_detail(date, order_id, stock_id, stock_name, status, deal_price, deal_num, deal_time)
                else:
                    # [[date, stock_id, stock_name, hold_status, origin_price, total_num, origin_amount,
                    #   current_amount, yesterday_num, nowadays_num, available_num, holding_profit, deal_profit]],
                    # columns = ['交易日', '证券代码', '证券名称', '持仓方向', '持仓成本价', '总持仓股数',
                    # '持仓成本金额', '当前总持仓金额', '昨日持仓', '今日持仓', '可用持仓', '持仓盈亏', '交易盈亏']
                    # 新增
                    total_num = order_num
                    # 持仓成本金额
                    origin_amount = order_num * order_price_new
                    # 当前总持仓金额,回测拿的是后一个交易日的收盘价做实时价格
                    vs_price = float(t_s.iloc[-1, 2])
                    current_amount = total_num * vs_price
                    # 持仓成本价，order_price
                    origin_price = float(origin_amount / total_num)
                    yesterday_num = 0
                    nowadays_num = total_num
                    available_num = 0
                    # 当前持仓盈亏
                    holding_profit = int(current_amount - origin_amount)
                    # 交易盈亏
                    org = data_process.get_holding_without_0_back()
                    if stock_id in np.array(org.iloc[:, 1]):
                        deal_profit = origin.iloc[0, -1]
                    else:
                        deal_profit = 0
                    # 调用当日持仓函数
                    obj_0.current_holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                                 origin_amount,
                                                 current_amount, yesterday_num, nowadays_num, available_num,
                                                 holding_profit, deal_profit)
                    # [[date, order_id, stock_id, stock_name, order_status, order_price, order_num, lock_amount,
                    #   deal_amount, deal_num, order_time, deal_status]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '委托行为', '委托价格',
                    #            '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
                    origin = order_stock_detail.loc[order_stock_detail.iloc[:, 2] == stock_id, :]
                    origin1 = origin.loc[origin.iloc[:, 5] == order_price, :]
                    order_id = origin1.iloc[0, 1]
                    order_status = origin1.iloc[0, 4]
                    lock_amount = origin1.iloc[0, 7]
                    # change below 3
                    deal_amount = order_price_new
                    deal_num = order_num
                    deal_status = 'deal'
                    # 调当日委托函数，变化交易状态，只改一条数据
                    obj_0.current_place_order(date, order_id, stock_id, stock_name, order_status, order_price,
                                              order_num, lock_amount,
                                              deal_amount, deal_num, order_time, deal_status)
                    # 委托卖出时，除了正常股价还有服务费要锁定
                    commission_buy, commission_sell = obj_3.order_cost(deal_num, order_price_new, close_tax=0.001,
                                                                       open_commission=0.0003,
                                                                       close_commission=0.0003, min_commission=5)
                    # 原锁定金额减去成交费率和成交总金额的和
                    lock_amount_undeal = round((lock_amount - (order_price_new * deal_num + commission_buy)), 2)
                    if lock_amount_undeal != 0:
                        deal_amount_undeal = 0
                        deal_num_undeal = 0
                        # 部分未成交但锁定的金额
                        deal_status = 'undeal'
                        obj_0.current_place_order(date, order_id, stock_id, stock_name, order_status, order_price,
                                                  order_num, lock_amount_undeal,
                                                  deal_amount_undeal, deal_num_undeal, order_time, deal_status)
                    # [[date, order_id, stock_id, stock_name, deal_status, deal_price, deal_num,
                    #   deal_time]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '交易行为', '成交价格',
                    #            '成交数量', '成交时间'])
                    deal_price = order_price_new
                    deal_time = order_time
                    status = 'buy'
                    # 调用当日成交函数
                    obj_0.current_deal_detail(date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                              deal_time)
                    # 调用历史成交函数
                    obj_1.deal_detail(date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                      deal_time)
                    # [[stock_id, stock_name, first_buy_time, last_sell_time, holding_period, origin_price, last_price,
                    # current_price,deal_profit]],
                    # columns = ['证券代码', '证券名称', '首次买入时间', '清仓时间', '持仓时间', '首次买入价', '清仓价', '当前价','总盈亏 '])
                    first_buy_time = date
                    last_sell_time = 'unknown'
                    last_price = 'unknown'
                    holding_period = 'unknown'
                    status = 'undeal'
                    refused_reason = 'unknown'
                    current_price = vs_price
                    # 调账户盈利情况
                    obj_2.total_profit(stock_id, stock_name, first_buy_time, last_sell_time, holding_period,
                                       origin_price, last_price, current_price, deal_profit, status, refused_reason)

        # 如果委托状态是'sell'
        # 记住每卖一次，持仓盈亏计算的是剩下的
        # 委卖时的价格必须到达过才能算成交
        # 不管价格高低，都会在挂单价成交
        if update_high >= order_price >= update_low:
            # if order_price < update_open:
            #     # 拿开盘价替代
            #     order_price_new = update_open
            if order_stock_detail.iloc[i, 4] == 'sell':
                # date = date_star
                # order_time = time.strftime("%H:%M:%S", time.localtime())
                hold_status = 'sell'
                # 如果是已持有的股票
                if stock_id in np.array(current_holding_detail.iloc[:, 1]):
                    # [[date, stock_id, stock_name, hold_status, origin_price, total_num, origin_amount,
                    #   current_amount, yesterday_num, nowadays_num, available_num, holding_profit, deal_profit]],
                    # columns = ['交易日', '证券代码', '证券名称', '持仓方向', '持仓成本价', '总持仓股数',
                    # '持仓成本金额', '当前总持仓金额', '昨日持仓', '今日持仓', '可用持仓', '持仓盈亏', '交易盈亏']
                    # 委托卖出时，除了正常股价还有服务费印花税等要扣除,包含在卖出股票金额里面
                    commission_buy, commission_sell = obj_3.order_cost(order_num, order_price, close_tax=0.001,
                                                                       open_commission=0.0003,
                                                                       close_commission=0.0003, min_commission=5)
                    # 减法
                    origin2 = current_holding_detail.loc[current_holding_detail.iloc[:, 1] == stock_id, :]
                    # 考虑当日买入的不能卖出，否则卖出不够为负值的情况
                    available_num = origin2.iloc[0, -3] - order_num
                    if available_num < 0:
                        available_num = 0
                        order_num = origin2.iloc[0, -3]
                        if order_num == 0:
                            print stock_id, '当日已无可卖股数'
                            continue
                    total_num = origin2.iloc[0, 5] - order_num
                    vs_price = float(t_s.iloc[-1, 2])
                    # 持仓成本金额 ------成本金额和成本价是会随买入卖出而变化的，但不会随着股价涨跌而变化
                    # 每次卖出交易都会更新一次持仓成本金额
                    # 以卖出时的order_price_new为新的成本价计算
                    origin_amount = float(total_num * origin2.iloc[0, 4])
                    # 当前总持仓金额,回测拿的是后一个交易日的收盘价做实时价格
                    current_amount = total_num * vs_price
                    yesterday_num = origin2.iloc[0, 8]
                    nowadays_num = total_num
                    # 持仓盈亏，剩余的持仓成本金额，包括了盈亏的金额，也考虑了total_num=0的情况
                    holding_profit = int(current_amount - origin_amount)
                    # 交易盈亏，委托价和成本价的价差乘以委托笔数，减去交易费
                    deal_profit = round(((order_price - origin2.iloc[0, 4]) * order_num - commission_sell + origin2.iloc[0, -1]), 2)
                    # 持仓成本价
                    # 调def total_profit()，调用历史持仓函数，一旦清空，要调持仓，并删除个股
                    if total_num == 0:
                        origin_price = 0
                        # deal_profit = round(((order_price - origin2.iloc[0, 4]) * order_num - commission_sell), 2)
                        # 调用历史持仓函数,只有结清时才会调用
                        obj_1.holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                             origin_amount,
                                             current_amount, yesterday_num, nowadays_num, available_num, holding_profit,
                                             deal_profit)
                        # [[stock_id, stock_name, first_buy_time, last_sell_time, holding_period, origin_price,
                        # last_price, current_price,deal_profit, status]],
                        # columns = ['证券代码', '证券名称', '首次买入时间', '清仓时间', '持仓时间', '首次买入价', '清仓价', '当前价','总盈亏','状态'])
                        total_profit = data_process.get_total_profit_back()
                        first_buy_time = total_profit.loc[total_profit.iloc[:, 0] == stock_id, :]
                        first_buy_time_0 = first_buy_time.loc[first_buy_time.iloc[:, -2] == 'undeal', :]
                        first_buy_time_1 = str(first_buy_time_0.iloc[0, 2])
                        last_sell_time = date
                        # 计算时间差
                        z = time.strptime(last_sell_time, "%Y%m%d")
                        y, m, d = z[0:3]
                        last = datetime.datetime(y, m, d)

                        a = time.strptime(first_buy_time_1, "%Y%m%d")
                        y, m, d = a[0:3]
                        first = datetime.datetime(y, m, d)
                        holding_period = (last - first).days
                        origin_price_0 = first_buy_time_0.iloc[0, 5]
                        last_price = order_price
                        current_price = vs_price
                        status = 'deal'
                        bag = []
                        obj_4 = Calculation_back(stock_id, bag, date_star)
                        bag, refused_reason = obj_4.stocks_choose_for_sale()
                        reason = ''
                        for r in refused_reason:
                            reason += str(r)
                        if refused_reason == []:
                            reason = '清仓价清仓'
                        # 调账户个股盈利函数
                        obj_2.total_profit(stock_id, stock_name, first_buy_time_1, last_sell_time, holding_period,
                                           origin_price_0, last_price, current_price, deal_profit, status,
                                           reason)
                    else:
                        origin_price = origin_amount / total_num
                    # 调用当日持仓函数,一旦清空，要删除个股
                    obj_0.current_holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                                 origin_amount,
                                                 current_amount, yesterday_num, nowadays_num, available_num,
                                                 holding_profit, deal_profit)
                    # [[date, order_id, stock_id, stock_name, order_status, order_price, order_num, lock_amount,
                    #   deal_amount, deal_num, order_time, deal_status]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '委托行为', '委托价格',
                    #            '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
                    origin = order_stock_detail.loc[order_stock_detail.iloc[:, 2] == stock_id, :]
                    origin3 = origin.loc[origin.iloc[:, 5] == order_price, :]
                    order_id = origin3.iloc[0, 1]
                    order_status = 'sell'
                    lock_amount = round((order_price * order_num - commission_sell), 2)
                    # change below 3
                    deal_amount = order_price
                    deal_num = order_num
                    deal_status = 'deal'
                    # 调当日委托函数，变化交易状态，只改一条数据
                    obj_0.current_place_order(date, order_id, stock_id, stock_name, order_status, order_price,
                                              order_num, lock_amount,
                                              deal_amount, deal_num, order_time, deal_status)
                    # [[date, order_id, stock_id, stock_name, deal_status, deal_price, deal_num,
                    #   deal_time]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '交易行为', '成交价格',
                    #            '成交数量', '成交时间'])
                    deal_price = order_price
                    deal_time = order_time
                    status = 'sell'
                    # 调用当日成交函数
                    obj_0.current_deal_detail(date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                              deal_time)
                    # 调用历史成交函数
                    obj_1.deal_detail(date, order_id, stock_id, stock_name, status, deal_price, deal_num,
                                      deal_time)
        time.sleep(10)
    time.sleep(10)
    print '**当日结算**'
    # 更新帐户表,无论买入或卖出成功与否都需要在这个时间点更新帐户表
    # 读库
    holding_stock_detail = data_process.get_holding_stock_detail_current_back()
    # 持仓数据更新，列出实时买卖的股票列表
    stock_hold = np.array(holding_stock_detail.iloc[:, 1].values)
    for stock in stock_hold:
        date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
        # 数据类型转换
        date_star1 = date_star0 + datetime.timedelta(1)
        date_star_start = date_star1.strftime('%Y-%m-%d')
        # 数据类型转换，用了-8，考虑国内最长假期为7天
        date_star2 = date_star0 + datetime.timedelta(8)
        date_star_end = date_star2.strftime('%Y-%m-%d')
        error, t_s = get_h_data(stock, date_star_start, date_star_end)
        while error != 0:
            print 'tushare通道阻塞'
            time.sleep(100)
            error, t_s = get_h_data(stock, date_star_start, date_star_end)
        if t_s.empty:
            continue
        origin = holding_stock_detail.loc[holding_stock_detail.iloc[:, 1] == stock, :]
        total_num = origin.iloc[0, 5]
        if total_num == 0:
            continue
        time.sleep(10)
        date = date_star
        stock_name = origin.iloc[0, 2]
        hold_status = origin.iloc[0, 3]
        origin_price = origin.iloc[0, 4]
        origin_amount = origin.iloc[0, 6]
        vs_price = round((t_s.iloc[-1, 2]), 2)
        current_amount = total_num * vs_price
        # 把当日总股数，做次日的昨日股数
        yesterday_num = total_num
        nowadays_num = origin.iloc[0, 9]
        # 把当日总股数，做次日可用股数
        available_num = total_num
        # 持仓盈亏
        holding_profit = int(current_amount - origin_amount)
        # 交易盈亏
        deal_profit = origin.iloc[0, -1]
        # 调用当日持仓函数
        obj_0.current_holding_detail(date, stock, stock_name, hold_status, origin_price, total_num,
                                     origin_amount,
                                     current_amount, yesterday_num, nowadays_num, available_num,
                                     holding_profit, deal_profit)
    # 读取更新后的数据
    holding_stock_detail = data_process.get_holding_stock_detail_current_back()
    order_stock_detail = data_process.get_order_stock_detail_current_back()

    # order_id = 0 代表可用金额不用删除固定的锁定金额
    order_id = 0
    # 帐户表Account更新
    obj_2.account_detail(order_id, holding_stock_detail, order_stock_detail, date_star)
    # [[date, current_amount, holding_profit_yesterday, holding_profit_today, nowadays_profit, week_profit,
    # month_profit]]
    # columns = ['日期', '当日总持仓金额', '昨日持仓盈亏', '今日持仓盈亏', '当日盈亏', '近5日盈亏', '近20日盈亏']
    date = date_star
    # 读账单表
    account_data = data_process.get_account_back()
    total_current_amount = account_data.iloc[0, -1]
    # 读账户盈利情况表
    account_condition = data_process.get_account_profit_back()
    # 昨日持仓盈亏 = 昨天的，今日持仓盈亏
    # 今日持仓盈亏，之后加了一个交易盈亏，更直观一点
    holding_profit_yesterday = account_condition.iloc[-1, 3]
    if holding_stock_detail.iloc[:, -2].sum():
        nowadays_profit = holding_stock_detail.iloc[:, -2].sum() + holding_stock_detail.iloc[:, -1].sum()
    else:
        nowadays_profit = 0
    # 近5日盈亏
    if len(account_data) < 5:
        week_profit = 0
    else:
        week_profit = account_condition.iloc[-5:, 3].sum() / 5.0
    # 近20日盈亏
    if len(account_data) < 20:
        month_profit = 0
    else:
        month_profit = account_condition.iloc[-20:, 3].sum() / 20.0
    # 调账户盈利情况表
    obj_2.time_profit(date, total_current_amount, holding_profit_yesterday, nowadays_profit, week_profit, month_profit)
    # 第一行全存0

    end = datetime.datetime.now()
    secondsDiff = (end - start).seconds
    minutesDiff = round(secondsDiff / 60, 1)
    print 'hold_or_not_secondsDiff_2', secondsDiff


def clear_db():
    start = datetime.datetime.now()

    data_process.delete_current_order_back()
    data_process.delete_current_deal_back()
    data_process.delete_current_hold_0_back()

    end = datetime.datetime.now()
    secondsDiff = (end - start).seconds
    minutesDiff = round(secondsDiff / 60, 1)
    print 'clear_db_secondsDiff_2', secondsDiff


def holding_translated():
    """
    # 不满足选股条件的持仓股票进行清仓
    :return: 
    """
    start = datetime.datetime.now()
    obj_0 = Current()
    obj_1 = History()
    obj_3 = Deal()

    # 读当日委托表和数据更新表
    current_holding_detail = data_process.get_holding_stock_detail_current_back()

    # 列出实时买卖的股票列表
    stock_hold = np.array(current_holding_detail.iloc[:, 1].values)
    # 因为是二次委托，给一个订单编号
    order_id = 3
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    bad_package = []
    for stock in stock_hold:
        bag = []
        obj = Calculation_back(stock, bag, date_star)
        bag, refused_reason = obj.stocks_choose_for_sale()
        # 如果没有被选中
        if len(bag) == 0:
            bad_package.append(stock)
            # 委卖
            # 回测持仓股破型就用次工作日的开盘价做委卖价
            date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
            # 数据类型转换
            date_star1 = date_star0 + datetime.timedelta(1)
            date_star_start = date_star1.strftime('%Y-%m-%d')
            # 数据类型转换，用了-8，考虑国内最长假期为7天
            date_star2 = date_star0 + datetime.timedelta(8)
            date_star_end = date_star2.strftime('%Y-%m-%d')
            # t_s = ts.get_h_data(stock, start=date_star_start, end=date_star_end, autype='qfq', drop_factor=False)
            error, t_s = get_h_data(stock, date_star_start, date_star_end)
            while error != 0:
                time.sleep(100)
                error, t_s = get_h_data(stock, date_star_start, date_star_end)
            if t_s.empty:
                continue
            price = float(t_s.iloc[-1, 0])
            if price == 0:
                print stock, u'停牌'
                continue
            num_offer = current_holding_detail.loc[current_holding_detail.iloc[:, 1] == stock, ]
            num = num_offer.iloc[0, -3]
            if num == 0:
                continue
            order_price = price
            order_num = num
            order_status = 'sell'
            date = date_star
            order_time = time.strftime("%H:%M:%S", time.localtime())
            stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[
                0]
            # 委托买入时，除了正常股价还有服务费要锁定
            commission_buy, commission_sell = obj_3.order_cost(order_num, order_price, close_tax=0.001,
                                                               open_commission=0.0003, close_commission=0.0003,
                                                               min_commission=5)
            # 卖的时候是减commission_sell，因为锁定后成交的话，手续费是从卖出金额中扣除的
            lock_amount = round((order_num * order_price - commission_sell), 2)
            deal_amount = 0
            deal_num = 0
            deal_status = 'undeal'
            # 委托下单,当日委托表更新
            obj_0.current_place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                                      lock_amount,  deal_amount, deal_num, order_time, deal_status)
            # 历史委托表更新
            obj_1.place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                              lock_amount,  deal_amount, deal_num, order_time, deal_status)

    end = datetime.datetime.now()
    seconds_diff = (end - start).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'second_order_seconds_diff', seconds_diff

    return bad_package


def get_date_list(start_time, end_time):
    start_date = datetime.datetime(int(start_time[0:4]), int(start_time[4:6]), int(start_time[6:8]))
    date_list = []
    days = start_date
    day = start_time
    while 1:
        if day < end_time:
            if days.weekday() == 4:  # friday
                days = days + datetime.timedelta(days=3)
                day = days.strftime('%Y%m%d')
                if day > end_time:
                    break
            elif days.weekday() == 5:  # sat
                days = days + datetime.timedelta(days=2)
                day = days.strftime('%Y%m%d')
                if day > end_time:
                    break
            else:
                days = days + datetime.timedelta(days=1)
                day = days.strftime('%Y%m%d')
            date_list.append(day)
        else:
            break
    return date_list


if __name__ == '__main__':
    # ###################给出回测时间段##################
    # date_start = '20170102'
    # date_end = '20170107'
    # date_start = '20161230'
    # date_end = '20170126'
    # # ###################创建时间表####################
    # # list为(.....]的所有工作日
    # date_list = get_date_list(date_start, date_end)
    # print date_list
    # for date_star in date_list:
    #     # 根据上证指数判断是否为假期或周末
    #     date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
    #     date_star_start = date_star0.strftime('%Y-%m-%d')
    #
    #     error, t_s = get_h_data('000001', date_star_start, date_star_start)
    #     while error != 0:
    #         time.sleep(100)
    #         error, t_s = get_h_data('000001', date_star, date_star)
    #     if t_s.empty:
    #         continue
    #     # ###################清空变型的持仓股###########
    #     # package = holding_translated()
    #     # ##################选股###################
    #     obj = Box()
    #     obj.create_box(date_star)
    #     # ##################委托###################
    #     import string
    #     box = data_process.get_box_back()
    #     box = str(np.array(box.iloc[-1, 1]))
    #     box = box.translate(None, string.punctuation).split()
    #     if str(box[0])[0] == 'u':
    #         list = []
    #         for i in range(len(box)):
    #             val = str(box[i])[1:]
    #             list.append(val)
    #     else:
    #         list = box
    #     # list = ['601000', '300030']
    #     stocks_order(box=list, bad_package=package)
    #     time.sleep(50)
    #     # #################刷新表单数据######################
    #     deal_check2()
    #     # #################清空部分表单数据##################
    #     clear_db()

    # ###########################单日测试#################################
    # date_star = '20161230'
    # package = holding_translated()
    # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[0, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # list = ['600416']
    # package = ['600112']
    # list = ['002265', '300106', '300139', '000502', '000150', '600495', '300209']
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170103'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[0, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # # list = []
    # # package = []
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170104'
    # package = holding_translated()
    # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[1, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()
    #
    # # ###########################单日测试#################################
    # date_star = '20170105'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[2, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170106'
    # package = holding_translated()
    # # print package
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[3, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()
    #
    # # ###########################单日测试#################################
    # date_star = '20170109'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[4, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()
    #
    # # ###########################单日测试#################################
    # date_star = '20170110'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[5, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(20)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170111'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[6, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(20)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################这一天买入很多，因为策略关系加上大盘萎靡，买入越多亏损越多，选股中大部分禁不起跌
    # date_star = '20170112'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[7, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(20)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170113'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[8, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(20)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170116'
    # package = holding_translated()
    # package = ['000014','002560','600716','600712','600792','300018','600375','002100','300407','600399','000032','300478','300470','600210','002327','000777','000069','002645','600509','002398','002658','002661','600482','600222','601258','002357']
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[9, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(20)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170117'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[10, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170118'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[11, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170119'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[12, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170120'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[13, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170123'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[14, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170124'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[15, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170125'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[16, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170126'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[17, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170203'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[18, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170206'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[19, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170207'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[20, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170208'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[21, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170209'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[22, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170210'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[23, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170213'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[24, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170214'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[25, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170215'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[26, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170216'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[27, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170217'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[28, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170220'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[29, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170221'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[30, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170222'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[31, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170223'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[32, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170224'
    # package = holding_translated()
    # # package = []
    # import string
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[33, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list,  bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170227'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[34, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170228'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[35, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170301'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[36, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170302'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[37, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170303'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[38, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    # date_star = '20170306'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[39, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170307'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[40, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170308'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[41, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # # ###########################单日测试#################################
    # date_star = '20170309'
    # package = holding_translated()
    # # package = []
    # import string
    #
    # box = data_process.get_box_back()
    # box = str(np.array(box.iloc[42, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # stocks_order(box=list, bad_package=package)
    # time.sleep(10)
    # # #################刷新表单数据######################
    # deal_check2()
    # clear_db()

    # ###########################单日测试#################################
    date_star = '20170310'
    package = holding_translated()
    # package = []
    import string

    box = data_process.get_box_back()
    box = str(np.array(box.iloc[43, 1]))
    box = box.translate(None, string.punctuation).split()
    if str(box[0])[0] == 'u':
        list = []
        for i in range(len(box)):
            val = str(box[i])[1:]
            list.append(val)
    else:
        list = box
    stocks_order(box=list, bad_package=package)
    time.sleep(10)
    # #################刷新表单数据######################
    deal_check2()
    clear_db()
