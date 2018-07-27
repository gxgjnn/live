# -*- coding: utf-8 -*-

from STOCK_CHOOSE.stock_box import Calculation
from DEAL.strategy2_initial import Initial
from apscheduler.schedulers.blocking import BlockingScheduler
from utils.newdata_achieve import *
from SIMULATION.deal_windows import *
from DEAL.deal import Deal
from DEAL.strategy2_vs import VS
from DEAL.info_online import *
import logging
logging.basicConfig()
import string


# 每个交易日收盘6：30pm
def update_database():
    """
    # 更新数据库
    :return: 
    """
    start = datetime.datetime.now()

    date = get_old_date()
    process_data(date, stock_code_queue)
    # 因时间问题现使用get_real_quotes(),因此新增了停牌和刚上市的股票，需要删除
    data_process.delete_0()

    end0 = datetime.datetime.now()
    seconds_diff = (end0 - start).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'update_database_minutes_diff', minutes_diff

    obj_6.create_box()
    end1 = datetime.datetime.now()
    seconds_diff = (end1 - end0).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'create_box_minutes_diff', minutes_diff


class Box(Account):

    def create_box(self):
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
            obj_5 = Calculation(stock, stock_box)
            obj_5.stocks_choose()
            print 'stock', stock
            print 'stock_box', stock_box
            print '*' * 30
        # stock_box = ['600459', '000989']
        stock_box = str(stock_box)
        tik = time.strftime("%Y-%m-%d", time.localtime())
        stocks_chosen_daily = pd.DataFrame([[tik, stock_box]], columns=['date', 'stocks_chosen_daily'])
        stocks_chosen_daily.to_sql(con=self.engine, name="stocks_chosen_daily", if_exists='append', index=False)
        print 'first', stock_box

        end = datetime.datetime.now()
        seconds_diff = (end - start).seconds
        minutes_diff = round(seconds_diff / 60, 1)
        print 'create_box_minutes_diff', minutes_diff

    def holding_translated(self):
        """
        # 不满足选股条件的持仓股票进行清仓
        :return: 
        """
        start = datetime.datetime.now()
        obj_0 = Current()
        obj_1 = History()
        obj_3 = Deal()

        # 读当日委托表和数据更新表
        current_holding_detail = data_process.get_holding_stock_detail_current()

        # 列出实时买卖的股票列表
        stock_hold = np.array(current_holding_detail.iloc[:, 1].values)
        # 因为是二次委托，给一个订单编号
        order_id = 3
        stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                       dtype={'code': np.str})
        bad_package = []
        for stock in stock_hold:
            bag = []
            obj = Calculation(stock, bag)
            bag, refused_reason = obj.stocks_choose_for_sale()
            if len(bag) == 0:
                bad_package.append(stock)
                # 委卖
                error, t_s = get_realtime_quotes(stock)
                while error != 0:
                    time.sleep(100)
                    error, t_s = get_realtime_quotes(stock)
                price = float(t_s.price[0])
                if price == 0:
                    print stock, u'停牌'
                    continue
                num_offer = current_holding_detail.loc[current_holding_detail.iloc[:, 1] == stock,]
                num = num_offer.iloc[0, -3]
                if num == 0:
                    continue
                order_price = price
                order_num = num
                order_status = 'sell'
                date = time.strftime("%Y-%m-%d", time.localtime())
                order_time = time.strftime("%H:%M:%S", time.localtime())
                stock_name = \
                str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[
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
                                          lock_amount, deal_amount, deal_num, order_time, deal_status)
                # 历史委托表更新
                obj_1.place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                                  lock_amount, deal_amount, deal_num, order_time, deal_status)

        package_box = str(bad_package)
        tik = time.strftime("%Y-%m-%d", time.localtime())
        holding_bad_package_daily = pd.DataFrame([[tik, package_box]], columns=['date', 'holding_bad_package_daily'])
        holding_bad_package_daily.to_sql(con=self.engine, name="holding_bad_package_daily", if_exists='replace', index=False)

        end = datetime.datetime.now()
        seconds_diff = (end - start).seconds
        minutes_diff = round(seconds_diff / 60, 1)
        print 'second_order_seconds_diff', seconds_diff
        return bad_package


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
    holding_stock_detail = data_process.get_holding_stock_detail_current()
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    order_id = 1
    for stock in box:
        # print stock
        # 拿当前价来作为可买股数的依据，虽说差距不大，但有些冒失
        error, t_s = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, t_s = get_realtime_quotes(stock)

        price = float(t_s.price[0])
        num_sell, available_money = trade_data(stock)
        num_buy = num_transfer(available_money, num_sell, price)
        obj_4 = Initial(stock, num_buy=num_buy, num_sell=num_sell)
        order_sell, order_buy = obj_4.quoting()
        # 挂单操作
        if order_buy.empty:
            print '选股订单买入委托为空，原因为报价大于实价后的报价纠正'
            continue
        # 挂买单跟新昨天委托表
        for i in range(len(order_buy)):
            date = time.strftime("%Y-%m-%d", time.localtime())
            order_time = time.strftime("%H:%M:%S", time.localtime())
            # stock_name = list(stock_basic_list.loc[stock_basic_list.code == stock, 'name'])[0]
            stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[0]
            order_status = 'buy'
            order_price = round((np.array(order_buy.price_buy)[i]), 2)
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
            time.sleep(2)
    # 读库
    order_stock_detail = data_process.get_order_stock_detail_current()
    # 帐户表Account更新
    obj_2.account_detail(order_id, holding_stock_detail, order_stock_detail)

    ware = holding_stock_detail.iloc[:, 1]
    new_ware = set(ware.values)-set(bad_package)
    for stock in new_ware:
        stock = str(stock).zfill(6)
        # 拿当前价来作为可买股数的依据，虽说差距不大，但有些冒失
        error, t_s = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, t_s = get_realtime_quotes(stock)
        price = float(t_s.price[0])
        num_sell, available_money = trade_data(stock)
        num_buy = num_transfer(available_money, num_sell, price)
        obj_4 = Initial(stock, num_buy=num_buy, num_sell=num_sell)
        order_sell, order_buy = obj_4.quoting()
        # 挂单操作
        if order_sell.empty:
            print '持仓卖单委托为空，原因为报价大于实价后的报价纠正'
            continue
        # 挂卖单append到今日委托表
        for i in range(len(order_sell)):
            date = time.strftime("%Y-%m-%d", time.localtime())
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
            # time.sleep(2)
            # 卖出委托不需要更新帐户表；因为卖出百分比定死，这里不改变持仓表可用持仓的数值

    end = datetime.datetime.now()
    seconds_diff = (end - start).seconds
    # minutes_diff = round(seconds_diff / 60, 1)
    print 'first_order_seconds_diff', seconds_diff


# 9：45
def trading():
    """
    # 每5分钟更新一次
    :return: 价格数据表
    """
    start = datetime.datetime.now()
    obj_2 = Account()
    order_stock_latest = pd.DataFrame()
    order_stock_detail = data_process.get_order_stock_detail_current()
    # 去重
    new_box = np.array(set(order_stock_detail.iloc[:, 2]))
    for stock in new_box:
        # vs_data = ts.get_realtime_quotes(stock)
        error, vs_data = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, vs_data = get_realtime_quotes(stock)
        vs_data = pd.concat([pd.DataFrame([stock], columns=['stock_id']), vs_data], 1)
        order_stock_latest = order_stock_latest.append(vs_data)
    # 存储
    order_stock_latest.to_sql(con=obj_2.engine, name="order_stock_latest", if_exists='replace', index=False)
    end = datetime.datetime.now()
    seconds_diff = (end - start).seconds
    # minutes_diff = round(seconds_diff / 60, 1)
    print 'order_stock_latest_seconds_diff', seconds_diff


# 11：35am
def deal_check():
    start = datetime.datetime.now()
    obj_0 = Current()
    obj_1 = History()
    obj_2 = Account()
    obj_3 = Deal()
    # 读当日委托表和数据更新表
    order_stock_latest = data_process.get_order_stock_latest()
    order_stock_detail = data_process.get_order_stock_detail_current()
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    # 挂单价 与 更新价比较
    for i in range(len(order_stock_detail.iloc[:, 2])):
        # 必须放在内层
        current_holding_detail = data_process.get_holding_without_0()
        stock_id = order_stock_detail.iloc[i, 2]
        order_price = order_stock_detail.iloc[i, 5]
        order_num = order_stock_detail.iloc[i, 6]
        date = time.strftime("%Y-%m-%d", time.localtime())
        order_time = time.strftime("%H:%M:%S", time.localtime())
        stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock_id, 'name']).split('    ')[1].split('\n')[0]
        # update_low = 19.99
        # update_high = 20.01
        update_open = float(order_stock_latest.loc[order_stock_latest.stock_id == stock_id, 'open'][0])
        update_high = float(order_stock_latest.loc[order_stock_latest.stock_id == stock_id, 'high'][0])
        update_low = float(order_stock_latest.loc[order_stock_latest.stock_id == stock_id, 'low'][0])
        order_price_new = float(order_price)
        if update_low <= order_price:
            if order_price > update_open:
                # 拿开盘价替代
                order_price_new = update_open
            # 如果委托状态是'buy'
            if order_stock_detail.iloc[i, 4] == 'buy':
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
                    # 当前总持仓金额
                    # vs_data = ts.get_realtime_quotes(stock_id)
                    error, vs_data = get_realtime_quotes(stock_id)
                    while error != 0:
                        time.sleep(100)
                        error, vs_data = get_realtime_quotes(stock_id)
                    current_amount = total_num * float(vs_data.price[0])
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
                    lock_amount = origin1.iloc[0, 7]
                    # change below 3
                    deal_amount = order_price_new
                    deal_num = order_num
                    deal_status = 'deal'
                    # 调当日委托函数，变化交易状态，只改一条数据
                    obj_0.current_place_order(date, order_id, stock_id, stock_name, order_status, order_price,
                                              order_num, lock_amount, deal_amount, deal_num, order_time, deal_status)
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
                    # 当前总持仓金额
                    # vs_price = ts.get_realtime_quotes(stock_id)
                    error, vs_price = get_realtime_quotes(stock_id)
                    while error != 0:
                        time.sleep(100)
                        error, vs_price = get_realtime_quotes(stock_id)
                    current_amount = total_num * float(vs_price.price[0])
                    # 持仓成本价，order_price
                    origin_price = round((origin_amount / total_num), 2)
                    yesterday_num = 0
                    nowadays_num = total_num
                    available_num = 0
                    # 当前持仓盈亏
                    holding_profit = int(current_amount - origin_amount)
                    # 交易盈亏
                    org = data_process.get_holding_without_0()
                    if stock_id in np.array(org.iloc[:, 1]):
                        deal_profit = origin.iloc[0, -1]
                    else:
                        deal_profit = 0
                    # 调用当日持仓函数
                    obj_0.current_holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                                 origin_amount, current_amount, yesterday_num, nowadays_num,
                                                 available_num, holding_profit, deal_profit)
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
                    current_price = float(vs_price.price[0])
                    # 调账户盈利情况
                    obj_2.total_profit(stock_id, stock_name, first_buy_time, last_sell_time, holding_period,
                                       origin_price, last_price, current_price, deal_profit, status, refused_reason)
            # 如果委托状态是'sell'
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
                    available_num = origin2.iloc[0, -3] - order_num
                    if available_num < 0:
                        available_num = 0
                        order_num = origin2.iloc[0, -3]
                        if order_num == 0:
                            print stock_id, '当日已无可卖股数'
                            continue
                    total_num = origin2.iloc[0, 5] - order_num
                    # 当前总持仓金额
                    # vs_price = ts.get_realtime_quotes(stock_id)
                    error, vs_price = get_realtime_quotes(stock_id)
                    while error != 0:
                        time.sleep(100)
                        error, vs_price = get_realtime_quotes(stock_id)
                    # 持仓成本金额 ------成本金额和成本价是会随买入卖出而变化的，但不会随着股价涨跌而变化
                    origin_amount = float(total_num * order_price)
                    current_amount = total_num * float(vs_price.price[0])
                    yesterday_num = origin2.iloc[0, 8]
                    nowadays_num = total_num
                    # 持仓盈亏，当前价减去成本价
                    holding_profit = int(current_amount - origin_amount)
                    # 交易盈亏，委托价和成本价的价差乘以委托笔数，减去交易费
                    deal_profit = round(((order_price - origin2.iloc[0, 4]) * order_num - commission_sell + origin2.iloc[0, -1]), 2)
                    # 持仓成本价
                    # 调def total_profit()，调用历史持仓函数，一旦清空，要调持仓，并删除个股
                    if total_num == 0:
                        origin_price = 0
                        # 调用历史持仓函数
                        obj_1.holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                             origin_amount, current_amount, yesterday_num, nowadays_num, available_num,
                                             holding_profit, deal_profit)
                        # [[stock_id, stock_name, first_buy_time, last_sell_time, holding_period, origin_price,
                        # last_price, current_price,deal_profit, status]],
                        # columns = ['证券代码', '证券名称', '首次买入时间', '清仓时间', '持仓时间', '首次买入价', '清仓价', '当前价','总盈亏','状态'])
                        total_profit = data_process.get_total_profit()
                        first_buy_time = total_profit.loc[total_profit.iloc[:, 0] == stock_id, :]
                        first_buy_time_0 = first_buy_time.loc[first_buy_time.iloc[:, -2] == 'undeal', :]
                        first_buy_time_1 = str(first_buy_time_0.iloc[0, 2])
                        last_sell_time = date
                        # 计算时间差
                        z = time.strptime(last_sell_time, "%Y-%m-%d")
                        y, m, d = z[0:3]
                        last = datetime.datetime(y, m, d)

                        a = time.strptime(first_buy_time_1, "%Y-%m-%d")
                        y, m, d = a[0:3]
                        first = datetime.datetime(y, m, d)
                        holding_period = (last - first).days
                        origin_price_0 = first_buy_time_0.iloc[0, 5]
                        last_price = order_price
                        current_price = float(vs_price.price[0])
                        status = 'deal'
                        bag = []
                        obj_4 = Calculation(stock_id, bag)
                        bag, refused_reason = obj_4.stocks_choose_for_sale()
                        reason = ''
                        for r in refused_reason:
                            reason += str(r)
                        if refused_reason == []:
                            reason = '清仓价清仓'
                        # 调账户个股盈利函数
                        obj_2.total_profit(stock_id, stock_name, first_buy_time_1, last_sell_time, holding_period,
                                           origin_price_0, last_price, current_price, deal_profit, status, reason)
                    else:
                        origin_price = round((origin_amount / total_num), 2)

                    # 调用当日持仓函数,一旦清空，要删除个股
                    obj_0.current_holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                                 origin_amount, current_amount, yesterday_num, nowadays_num,
                                                 available_num, holding_profit, deal_profit)
                    # [[date, order_id, stock_id, stock_name, order_status, order_price, order_num, lock_amount,
                    #   deal_amount, deal_num, order_time, deal_status]],
                    # columns = ['交易日', '任务编号', '证券代码', '证券名称', '委托行为', '委托价格',
                    #            '委托数量', '锁定金额', '成交价格', '成交数量', '下单时间', '定单状态'])
                    origin = order_stock_detail.loc[order_stock_detail.iloc[:, 2] == stock_id, :]
                    origin3 = origin.loc[origin.iloc[:, 5] == order_price, :]
                    order_id = origin3.iloc[0, 1]
                    order_status = 'sell'
                    # 以实际交易的为准
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
        # time.sleep(10)
    end = datetime.datetime.now()
    seconds_diff = (end - start).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'hold_or_not_seconds_diff_1', seconds_diff


# 2：55pm
# 1、挂新单，即满足函数条件的股票
def order_new_vs(bad_package):

    start = datetime.datetime.now()
    obj_0 = Current()
    obj_1 = History()
    obj_2 = Account()
    obj_3 = Deal()

    # 读当日委托表和数据更新表
    # order_stock_latest = data_process.get_order_stock_latest()
    order_stock_detail = data_process.get_order_stock_detail_current()
    current_holding_detail = data_process.get_holding_stock_detail_current()

    # 列出实时买卖的股票列表
    stock_box_0 = list(current_holding_detail.iloc[:, 1].values)
    stock_hold = list(set(stock_box_0) - set(bad_package))
    stock_hold_shadow = stock_hold
    stock_order = list(order_stock_detail.iloc[:, 2].values)
    stock_hold_shadow.extend(stock_order)
    new_box = list(set(stock_hold_shadow))
    # 因为是二次委托，给一个订单编号
    order_id = 2
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    for stock in new_box:
        error, t_s = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, t_s = get_realtime_quotes(stock)
        price = float(t_s.price[0])
        if price == 0:
            print stock, u'停牌'
            continue
        num_sell, available_money = trade_data(stock)
        num_buy = num_transfer(available_money, num_sell, price)
        obj_5 = Initial(stock, num_buy=num_buy, num_sell=num_sell)
        # current_vs_data = ts.get_realtime_quotes(stock)
        error, current_vs_data = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, current_vs_data = get_realtime_quotes(stock)
        obj_4 = VS(stock, obj_5)
        order_buy_vs = obj_4.buy_real_time(current_vs_data)
        # order_buy_vs = pd.DataFrame({'num':[300],'price':[19.30]})
        # 可能不止一个买价
        for i in range(len(order_buy_vs)):
            order_price = order_buy_vs.price[i]
            order_num = order_buy_vs.num[i]
            order_status = 'buy'
            date = time.strftime("%Y-%m-%d", time.localtime())
            order_time = time.strftime("%H:%M:%S", time.localtime())
            stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[0]
            if order_buy_vs.empty is False:
                # 挂单价 与 更新价比较
                if float(current_vs_data.low[0]) <= order_price:
                    # 此处只有买
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
                    obj_1.place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                                      lock_amount,
                                      deal_amount, deal_num, order_time, deal_status)
                    # time.sleep(5)
    # 更新帐户表
    # 读库
    holding_stock_detail = data_process.get_holding_stock_detail_current()
    order_stock_detail = data_process.get_order_stock_detail_current()
    # 帐户表Account更新
    obj_2.account_detail(order_id, holding_stock_detail, order_stock_detail)

    for stock in stock_hold:
        error, t_s = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, t_s = get_realtime_quotes(stock)
        price = float(t_s.price[0])
        if price == 0:
            print stock, u'停牌'
            continue
        num_sell, available_money = trade_data(stock)
        num_buy = num_transfer(available_money, num_sell, price)
        obj_5 = Initial(stock, num_buy=num_buy, num_sell=num_sell)
        # current_vs_data = ts.get_realtime_quotes(stock)
        error, current_vs_data = get_realtime_quotes(stock)
        while error != 0:
            time.sleep(100)
            error, current_vs_data = get_realtime_quotes(stock)
        obj_4 = VS(stock, obj_5)
        order_sell_vs = obj_4.sell_real_time(current_vs_data)
        # order_sell_vs = pd.DataFrame({'num':[300],'price':[19.30]})
        # 可能不止一个卖价
        for i in range(len(order_sell_vs)):
            order_price = order_sell_vs.price[i]
            order_num = order_sell_vs.num[i]
            order_status = 'sell'
            date = time.strftime("%Y-%m-%d", time.localtime())
            order_time = time.strftime("%H:%M:%S", time.localtime())
            stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[0]
            if order_sell_vs.empty is False:
                # 挂单价 与 更新价比较
                if float(current_vs_data.low[0]) <= order_price:
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
                    obj_1.place_order(date, order_id, stock, stock_name, order_status, order_price, order_num,
                                      lock_amount,
                                      deal_amount, deal_num, order_time, deal_status)
                    # time.sleep(5)
    end = datetime.datetime.now()
    seconds_diff = (end - start).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'second_order_seconds_diff', seconds_diff


# 3:10pm
def deal_check2():
    start = datetime.datetime.now()
    obj_0 = Current()
    obj_1 = History()
    obj_2 = Account()
    obj_3 = Deal()
    # 读当日委托表和数据更新表
    order_stock_latest = data_process.get_order_stock_latest()
    order_stock_detail = data_process.get_order_stock_detail_current()
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    order_stock_detail = order_stock_detail.loc[order_stock_detail.iloc[:, -1] != 'deal', ]
    # 挂单价 与 更新价比较
    for i in range(len(order_stock_detail.iloc[:, 2])):
        # 必须放在内层
        current_holding_detail = data_process.get_holding_without_0()
        stock_id = order_stock_detail.iloc[i, 2]
        order_price = order_stock_detail.iloc[i, 5]
        order_num = order_stock_detail.iloc[i, 6]
        stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock_id, 'name']).split('    ')[1].split('\n')[0]
        # update_low = 19.29
        # update_high = 19.31
        update_open = float(order_stock_latest.loc[order_stock_latest.stock_id == stock_id, 'open'][0])
        update_high = float(order_stock_latest.loc[order_stock_latest.stock_id == stock_id, 'high'][0])
        update_low = float(order_stock_latest.loc[order_stock_latest.stock_id == stock_id, 'low'][0])
        order_price_new = float(order_price)
        order_time = time.strftime("%H:%M:%S", time.localtime())
        if update_low <= order_price:
            if order_price > update_open:
                # 拿开盘价替代
                order_price_new = update_open
            # 如果委托状态是'buy'
            if order_stock_detail.iloc[i, 4] == 'buy':
                date = time.strftime("%Y-%m-%d", time.localtime())
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
                    # 当前总持仓金额
                    # vs_data = ts.get_realtime_quotes(stock_id)
                    error, vs_data = get_realtime_quotes(stock_id)
                    while error != 0:
                        time.sleep(100)
                        error, vs_data = get_realtime_quotes(stock_id)
                    current_amount = total_num * float(vs_data.price[0])
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
                    # 当前总持仓金额
                    # vs_price = ts.get_realtime_quotes(stock_id)
                    error, vs_price = get_realtime_quotes(stock_id)
                    while error != 0:
                        time.sleep(100)
                        error, vs_price = get_realtime_quotes(stock_id)
                    current_amount = total_num * float(vs_price.price[0])
                    # 持仓成本价，order_price
                    origin_price = round((origin_amount / total_num), 2)
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
                    refused_reason = 'unknown'
                    status = 'undeal'
                    current_price = float(vs_price.price[0])
                    # 调账户盈利情况
                    obj_2.total_profit(stock_id, stock_name, first_buy_time, last_sell_time, holding_period,
                                       origin_price, last_price, current_price, deal_profit, status, refused_reason)

            # 如果委托状态是'sell'
        if update_high >= order_price >= update_low:
            # if order_price < update_open:
            #     # 拿开盘价替代
            #     order_price_new = update_open
            if order_stock_detail.iloc[i, 4] == 'sell':
                # date = date_star
                # order_time = time.strftime("%H:%M:%S", time.localtime())
                hold_status = 'sell'
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
                    available_num = origin2.iloc[0, -3] - order_num
                    if available_num < 0:
                        available_num = 0
                        order_num = origin2.iloc[0, -3]
                        if order_num == 0:
                            print stock_id, '当日已无可卖股数'
                            continue
                    total_num = origin2.iloc[0, 5] - order_num
                    # 持仓成本金额 ------成本金额和成本价是会随买入卖出而变化的，但不会随着股价涨跌而变化
                    origin_amount = float(total_num * order_price)
                    # 当前总持仓金额
                    # vs_price = ts.get_realtime_quotes(stock_id)
                    error, vs_price = get_realtime_quotes(stock_id)
                    while error != 0:
                        time.sleep(100)
                        error, vs_price = get_realtime_quotes(stock_id)
                    current_amount = total_num * float(vs_price.price[0])
                    yesterday_num = origin2.iloc[0, 8]
                    nowadays_num = total_num
                    # 持仓盈亏，在之前持仓盈亏的基础上，加上卖出后持仓金额变化
                    holding_profit = int(current_amount - origin_amount)
                    # 交易盈亏，委托价和成本价的价差乘以委托笔数，减去交易费
                    deal_profit = round(((order_price - origin2.iloc[0, 4]) * order_num - commission_sell + origin2.iloc[0, -1]), 2)
                    # 持仓成本价
                    # 调def total_profit()，调用历史持仓函数，一旦清空，要调持仓，并删除个股
                    if total_num == 0:
                        origin_price = 0
                        # 调用历史持仓函数
                        obj_1.holding_detail(date, stock_id, stock_name, hold_status, origin_price, total_num,
                                             origin_amount,
                                             current_amount, yesterday_num, nowadays_num, available_num, holding_profit,
                                             deal_profit)
                        # [[stock_id, stock_name, first_buy_time, last_sell_time, holding_period, origin_price,
                        # last_price, current_price,deal_profit, status]],
                        # columns = ['证券代码', '证券名称', '首次买入时间', '清仓时间', '持仓时间', '首次买入价', '清仓价', '当前价','总盈亏','状态'])
                        total_profit = data_process.get_total_profit()
                        first_buy_time = total_profit.loc[total_profit.iloc[:, 0] == stock_id, :]
                        first_buy_time_0 = first_buy_time.loc[first_buy_time.iloc[:, -2] == 'undeal', :]
                        first_buy_time_1 = str(first_buy_time_0.iloc[0, 2])
                        last_sell_time = date
                        # 计算时间差
                        z = time.strptime(last_sell_time, "%Y-%m-%d")
                        y, m, d = z[0:3]
                        last = datetime.datetime(y, m, d)

                        a = time.strptime(first_buy_time_1, "%Y-%m-%d")
                        y, m, d = a[0:3]
                        first = datetime.datetime(y, m, d)
                        holding_period = (last - first).days
                        origin_price_0 = first_buy_time_0.iloc[0, 5]
                        last_price = order_price
                        current_price = float(vs_price.price[0])
                        status = 'deal'
                        bag = []
                        obj_4 = Calculation(stock_id, bag)
                        bag, refused_reason = obj_4.stocks_choose_for_sale()
                        reason = ''
                        for r in refused_reason:
                            reason += str(r)
                        if refused_reason == []:
                            reason = '清仓价清仓'
                        # 调账户个股盈利函数
                        obj_2.total_profit(stock_id, stock_name, first_buy_time_1, last_sell_time, holding_period,
                                           origin_price_0, last_price, current_price, deal_profit, status, reason)
                    else:
                        origin_price = round((origin_amount / total_num), 2)
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
        error, vs_data = get_realtime_quotes(stock_id)
        while error != 0:
            print 'tushare通道阻塞'
            time.sleep(100)
            error, vs_data = get_realtime_quotes(stock_id)
        origin = holding_stock_detail.loc[holding_stock_detail.iloc[:, 1] == stock, :]
        date = time.strftime("%Y-%m-%d", time.localtime())
        stock_name = origin.iloc[0, 2]
        hold_status = origin.iloc[0, 3]
        origin_price = origin.iloc[0, 4]
        total_num = origin.iloc[0, 5]
        origin_amount = origin.iloc[0, 6]
        current_amount = total_num * round((vs_data.price[0]), 2)
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
    holding_stock_detail = data_process.get_holding_stock_detail_current()
    order_stock_detail = data_process.get_order_stock_detail_current()
    # order_id = 0 代表可用金额不用删除固定的锁定金额
    order_id = 0
    # 帐户表Account更新
    obj_2.account_detail(order_id, holding_stock_detail, order_stock_detail)
    # [[date, current_amount, holding_profit_yesterday, holding_profit_today, nowadays_profit, week_profit,
    # month_profit]]
    # columns = ['日期', '当日总持仓金额', '昨日持仓盈亏', '今日持仓盈亏', '当日盈亏', '近5日盈亏', '近20日盈亏']
    date = time.strftime("%Y-%m-%d", time.localtime())
    # 读账单表
    account_data = data_process.get_account()
    total_current_amount = account_data.iloc[0, -1]
    # 读账户盈利情况表
    account_condition = data_process.get_account_profit()
    # 昨日持仓盈亏 = 昨天的，今日持仓盈亏
    holding_profit_yesterday = account_condition.iloc[-1, 3]
    if holding_stock_detail.iloc[:, -2].sum():
        nowadays_profit = holding_stock_detail.iloc[:, -2].sum()
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
    seconds_diff = (end - start).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'hold_or_not_seconds_diff_2', seconds_diff


def clear_db():
    start = datetime.datetime.now()

    data_process.delete_current_order()
    data_process.delete_current_deal()
    data_process.delete_current_hold_0()

    end = datetime.datetime.now()
    seconds_diff = (end - start).seconds
    minutes_diff = round(seconds_diff / 60, 1)
    print 'clear_db_seconds_diff_2', seconds_diff


def get_h_data(stock_id, start, end):
    e = 0
    try:
        t_s = ts.get_h_data(stock_id, start=start, end=end, autype='qfq', drop_factor=False)
    except Exception, e:
        t_s = pd.DataFrame()
        pass
    return e, t_s


def get_realtime_quotes(stock_id):
    e = 0
    try:
        t_s = ts.get_realtime_quotes(stock_id)
    except Exception, e:
        t_s = pd.DataFrame()
        pass
    return e, t_s


if __name__ == '__main__':
    # ###############9:15分委托#################
    # import string
    # # obj_6 = Box()
    # # obj_6.create_box()
    # box = data_process.get_box()
    # box = str(np.array(box.iloc[-1, 1]))
    # box = box.translate(None, string.punctuation).split()
    # stocks_order(box)
    # ################数据定时更新##################
    # trading()
    # ###################11:45刷新###################
    # deal_check()
    # #################14：55实时委托###################
    # order_new_vs()
    # ###################15:10收盘数据刷新######################
    # deal_check2()
    ###########################################################

    # BlockingScheduler
    #sched = BlockingScheduler()
    # Schedules job_function to be run on the third Friday
    # of June, July, August, November and December at 00:00, 01:00, 02:00 and 03:00
    # sched.add_job(job_function, 'cron', month='6-8,11-12', day='3rd fri', hour='0-3')
    # Runs from Monday to Friday at 5:30 (am) until 2014-05-30 00:00:00
    obj_6 = Box()
    update_database()
    # 6：30pm更新数据库，以及选股----【6点以后有数据可取，保险起见设为6：30pm，以5s为sleep间隔取数，耗时693分钟，预计至次日早上8：00数据库更新完毕】
    # 【在公司，更新数据库加上选股用了1058分钟，17.63个小时】
    # 【在家里，更新数据库用了554分钟，9小时，选股用了412分钟，7小时】
    #sched.add_job(update_database, 'cron', day_of_week='mon-fri', hour=19, minute=47)

    # time.sleep(100)------【选股花了415分钟，近7个小时】
    # obj_6 = Box()
    # obj_6.create_box()
    # sched.add_job(obj_6.create_box, 'cron', day_of_week='mon-fri', hour=9, minute=40)

    # # 9：15am委托下单
    # # # 读表
    # 对不满足于选股条件的持仓股票进行清仓
    # sched.add_job(obj_6.holding_translated, 'cron', day_of_week='mon-fri', hour=9, minute=35)
    # box_0 = data_process.get_package()
    # box_0 = str(np.array(box_0.iloc[-1, 1]))
    # box_0 = box_0.translate(None, string.punctuation).split()
    # if box_0 == []:
    #     package = []
    # else:
    #     if str(box_0[0])[0] == 'u':
    #         package = []
    #         for i in range(len(box_0)):
    #             val = str(box_0[i])[1:]
    #             list.append(val)
    #     else:
    #         package = box_0

    # box = data_process.get_box()
    # box = str(np.array(box.iloc[-1, 1]))
    # box = box.translate(None, string.punctuation).split()
    # if str(box[0])[0] == 'u':
    #     list = []
    #     for i in range(len(box)):
    #         val = str(box[i])[1:]
    #         list.append(val)
    # else:
    #     list = box
    # # stocks_order(box=list)
    # sched.add_job(stocks_order, 'cron', day_of_week='mon-fri', hour=9, minute=15, kwargs={'box': list, 'bad_package': package})
    #
    # # 11:30am刷新行情表
    # sched.add_job(trading, 'cron', day_of_week='mon-fri', hour=11, minute=35)
    #
    # # 11:45刷新委托表
    # sched.add_job(deal_check, 'cron', day_of_week='mon-fri', hour=11, minute=40)
    #
    # # 14：55委托下单
    # sched.add_job(order_new_vs, 'cron', day_of_week='mon-fri', hour=14, minute=55)
    #
    # # 15:05刷新行情表
    # sched.add_job(trading, 'cron', day_of_week='mon-fri', hour=15, minute=05)
    #
    # # 15:10刷新委托表
    # sched.add_job(deal_check2, 'cron', day_of_week='mon-fri', hour=15, minute=10)
    #
    # # 15:15清空当日委托表和当日成交表
    # sched.add_job(clear_db, 'cron', day_of_week='mon-fri', hour=15, minute=15)
    #
    #sched.start()
