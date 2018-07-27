# -*- coding: utf-8 -*-

import os
import time
import random
import datetime
from multiprocessing import Pool
from BACK_TRACE import main_back


def king(date_start, date_end):
    # ###################创建时间表####################
    # list为(.....]的所有工作日
    date_list = main_back.get_date_list(date_start, date_end)
    print date_list
    for date_star in date_list:
        # 根据上证指数判断是否为假期或周末
        date_star0 = datetime.datetime.strptime(date_star, '%Y%m%d')
        date_star_start = date_star0.strftime('%Y-%m-%d')

        error, t_s = main_back.get_h_data('000001', date_star_start, date_star_start)
        while error != 0:
            time.sleep(100)
            error, t_s = main_back.get_h_data('000001', date_star, date_star)
        if t_s.empty:
            continue
        # ###################清空变型的持仓股###########
        # package = holding_translated()
        # ##################选股###################
        obj = main_back.Box()
        obj.create_box(date_star)
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


def long_time_task(name, date_start, date_end):
    print 'Run task %s (%s)...' % (name, os.getpid())
    start = time.time()
    ###########################
    # time.sleep(random.random() * 3)
    king(date_start, date_end)
    ###########################
    end = time.time()
    print 'Task %s runs %0.2f seconds.' % (name, (end - start))


def s(i):
    print i
    return i
if __name__ == '__main__':
    # king('20161230', '20170126')
    start = datetime.datetime.now()
    print 'Parent process %s.' % os.getpid()
    p = Pool(2)
    # p.apply_async(king, args=('20161230', '20170103'))
    # p.apply_async(king, args=('20170103', '20170104'))
    # p.apply_async(king, args=('20170104', '20170105'))
    # p.apply_async(king, args=('20170105', '20170106'))
    #
    # p.apply_async(king, args=('20170106', '20170109'))
    # p.apply_async(king, args=('20170109', '20170110'))
    # p.apply_async(king, args=('20170110', '20170111'))
    # p.apply_async(king, args=('20170111', '20170112'))
    # p.apply_async(king, args=('20170112', '20170113'))
    # #
    # p.apply_async(king, args=('20170113', '20170116'))
    # p.apply_async(king, args=('20170116', '20170117'))
    # p.apply_async(king, args=('20170117', '20170118'))
    # p.apply_async(king, args=('20170118', '20170119'))
    # p.apply_async(king, args=('20170119', '20170120'))
    # #
    # p.apply_async(king, args=('20170120', '20170123'))
    # p.apply_async(king, args=('20170123', '20170124'))
    # p.apply_async(king, args=('20170124', '20170125'))
    # p.apply_async(king, args=('20170125', '20170126'))

    # p.apply_async(king, args=('20170126', '20170203'))
    # p.apply_async(king, args=('20170203', '20170206'))
    # p.apply_async(king, args=('20170206', '20170207'))
    # p.apply_async(king, args=('20170207', '20170208'))
    #
    # p.apply_async(king, args=('20170208', '20170209'))
    # p.apply_async(king, args=('20170209', '20170210'))

    # p.apply_async(king, args=('20170210', '20170213'))
    # p.apply_async(king, args=('20170213', '20170214'))
    # p.apply_async(king, args=('20170214', '20170215'))
    # p.apply_async(king, args=('20170215', '20170216'))
    #
    # p.apply_async(king, args=('20170216', '20170217'))
    # p.apply_async(king, args=('20170217', '20170220'))
    # p.apply_async(king, args=('20170220', '20170221'))
    # p.apply_async(king, args=('20170221', '20170222'))
    # p.apply_async(king, args=('20170222', '20170223'))
    # p.apply_async(king, args=('20170223', '20170224'))
    #
    # p.apply_async(king, args=('20170224', '20170227'))
    # p.apply_async(king, args=('20170227', '20170228'))
    # p.apply_async(king, args=('20170228', '20170301'))
    # p.apply_async(king, args=('20170301', '20170302'))
    # p.apply_async(king, args=('20170302', '20170303'))

    # p.apply_async(king, args=('20170303', '20170306'))
    # p.apply_async(king, args=('20170306', '20170307'))
    # p.apply_async(king, args=('20170307', '20170308'))
    # p.apply_async(king, args=('20170308', '20170309'))
    # p.apply_async(king, args=('20170309', '20170310'))
    #
    # p.apply_async(king, args=('20170310', '20170313'))
    # p.apply_async(king, args=('20170313', '20170314'))
    # p.apply_async(king, args=('20170314', '20170315'))
    # p.apply_async(king, args=('20170315', '20170316'))
    # p.apply_async(king, args=('20170316', '20170317'))

    # p.apply_async(king, args=('20170317', '20170320'))
    # p.apply_async(king, args=('20170320', '20170321'))
    # p.apply_async(king, args=('20170321', '20170322'))
    # p.apply_async(king, args=('20170322', '20170323'))
    # p.apply_async(king, args=('20170323', '20170324'))
    #
    # p.apply_async(king, args=('20170324', '20170327'))
    # p.apply_async(king, args=('20170327', '20170328'))
    # p.apply_async(king, args=('20170328', '20170329'))
    # p.apply_async(king, args=('20170329', '20170330'))
    # p.apply_async(king, args=('20170330', '20170331'))

    # p.apply_async(king, args=('20170331', '20170403'))
    # p.apply_async(king, args=('20170403', '20170404'))
    # p.apply_async(king, args=('20170404', '20170405'))
    # p.apply_async(king, args=('20170405', '20170406'))
    # p.apply_async(king, args=('20170406', '20170407'))

    # p.apply_async(king, args=('20170407', '20170410'))
    # p.apply_async(king, args=('20170410', '20170411'))
    # p.apply_async(king, args=('20170411', '20170412'))
    # p.apply_async(king, args=('20170412', '20170413'))
    # p.apply_async(king, args=('20170413', '20170414'))
    #
    # p.apply_async(king, args=('20170414', '20170417'))
    # p.apply_async(king, args=('20170417', '20170418'))
    # p.apply_async(king, args=('20170418', '20170419'))
    # p.apply_async(king, args=('20170419', '20170420'))
    # p.apply_async(king, args=('20170420', '20170421'))

    p.apply_async(king, args=('20170421', '20170424'))
    p.apply_async(king, args=('20170424', '20170425'))
    p.apply_async(king, args=('20170425', '20170426'))
    p.apply_async(king, args=('20170426', '20170427'))
    p.apply_async(king, args=('20170427', '20170428'))

    p.apply_async(king, args=('20170428', '20170502'))
    p.apply_async(king, args=('20170502', '20170503'))
    p.apply_async(king, args=('20170503', '20170504'))
    p.apply_async(king, args=('20170504', '20170505'))

    p.apply_async(king, args=('20170505', '20170508'))
    p.apply_async(king, args=('20170508', '20170509'))
    p.apply_async(king, args=('20170509', '20170510'))
    p.apply_async(king, args=('20170510', '20170511'))
    p.apply_async(king, args=('20170511', '20170512'))




    print 'Waiting for all subprocesses done...'
    p.close()
    p.join()
    print 'All subprocesses done.'

    end = datetime.datetime.now()
    secondsDiff = (end - start).seconds
    minutesDiff = round(secondsDiff / 60, 1)
    print 'multi_process_9_minutesDiff', minutesDiff


    # p = Pool(10)
    # res = p.apply_async(s, args=('1','2'))
    # p.close()
    # p.join()
    # print 'done'
