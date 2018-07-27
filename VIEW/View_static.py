# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from matplotlib.finance import candlestick_ohlc
import datetime as dt
from utils import data_process
from utils import create_data


def candle_k(data):
    """
    一定要更改均线值，不然均线会错误
    存在的问题：1 x轴日期包含非交易日和停牌日，如果遇到节假日，或者分钟级数据遇到收市,时间就不会连续；
               2 图为静态图；
               3 不能交互
               4 必须限定x轴日期范围
    :param data: 某只股票的数据集，不包括停牌数据
    :return: K线和成交量图
    """

    # drop the date index from the dateframe & make a copy
    datareshape = data.reset_index()
    # convert the datetime64 column in the dataframe to 'float days'
    datareshape['date'] = mdates.date2num(datareshape['date'].astype(dt.date))
    # clean day data for candle view
    datareshape.drop(['volume', 'amount', 'factor', 'code'], axis=1, inplace=True)
    # 填缺失值的行为，是停牌缺失还是列缺失
    datareshape = datareshape.reindex(columns=['date', 'open', 'high', 'low', 'close'])

    # 考虑不满足210天的股票
    # av1,av2长度为150
    av1 = create_data.ave_data_create(datareshape.close.values, MA1, date=len(datareshape))
    # av1.reverse()
    av2 = create_data.ave_data_create(datareshape.close.values, MA2, date=len(datareshape))
    # av2.reverse()
    sp = len(datareshape.date.values[MA2 - 1:])
    fig = plt.figure(facecolor='#07000d', figsize=(15, 10))

    ax1 = plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, axisbg='#07000d')
    candlestick_ohlc(ax1, datareshape.values[-sp:], width=.6, colorup='#ff1717', colordown='#53c156')
    Label1 = str(MA1) + ' SMA'
    Label2 = str(MA2) + ' SMA'

    ax1.plot(datareshape.date.values[-sp:], av1[-sp:], '#e1edf9', label=Label1, linewidth=1.5)
    ax1.plot(datareshape.date.values[-sp:], av2[-sp:], '#4ee6fd', label=Label2, linewidth=1.5)
    ax1.grid(True, color='w')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='w')
    plt.ylabel('Stock price and Volume')

    # 绘制成交量
    volume_min = 0
    ax1v = ax1.twinx()
    ax1v.fill_between(datareshape.date.values[-sp:], volume_min, data.volume.values[-sp:], facecolor='#00ffe8',
                      alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    # Edit this to 3, so it's a bit larger
    ax1v.set_ylim(0, 3 * data.volume.values.max())
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

    # 修饰 添加股票代码以及指定位置添加文字与箭头
    plt.suptitle(stock, color='w')
    # plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)

    # Mark big event
    # TODO: Make a real case here
    ax1.annotate('BreakNews!', (datareshape.date.values[90], av1[90]),
                 xytext=(0.8, 0.9), textcoords='axes fraction',
                 arrowprops=dict(facecolor='white', shrink=0.05),
                 fontsize=10, color='w',
                 horizontalalignment='right', verticalalignment='bottom')

    plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)

    plt.show()


def timestamp2datetime(timestamp, convert_to_local=False):
    """
    Converts UNIX timestamp to a datetime object. 
    """
    if isinstance(timestamp, (int, long, float)):
        dat = dt.datetime.utcfromtimestamp(timestamp)
        if convert_to_local:  # 是否转化为本地时间
            dat = dat + dt.timedelta(hours=8)  # 中国默认时区
        return dat
    return timestamp


if __name__ == "__main__":

    stock = '600335'
    df = data_process.Get_DataFrame(stock,'20171210')
    MA1 = 5
    MA2 = 60
    start_date = dt.date(2017, 4, 10)
    end_date = dt.date(2017, 12, 10)
    df.date = timestamp2datetime(df.date)
    df_raw = df.loc[df.date > start_date, :]
    # df_raw.date = timestamp2datetime(df_raw.date)
    df_raw = df_raw.loc[df_raw.date < end_date, :]
    candle_k(df_raw)
