# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import print_function
from pyecharts import Kline, Bar, Line, Grid, Overlap
from utils import data_process
import pandas as pd
from utils import create_data


def kline_js(name, df, prices_cols=None, ma=('ma10',), width=1600, height=750, kline_xaxis_pos='top', render_path=None):
    """
    一定要更改均线值，不然均线会错误
    分钟级别的也能做，且时间连续，但图形尺寸被限定，还可以添加很多东西
    @params:
    - name: str                      #图例名称
    - df:  pandas.DataFrame          #columns包含 prices_cols、‘volume’
    - prices_cols : list             #默认 [u'open', u'close', u'low', u'high']
    - ma=('ma10',): list or tuple    #移动平均周期
    - width=1600, height=750         # 默认图片大小
    - kline_xaxis_pos='top'          #k-line图例默认在上方
    - render_path： str              #html file path to save
    """
    if not prices_cols:
        prices_cols = [u'open', u'close', u'low', u'high']

    if not set(prices_cols+['volume']).issubset(set(df.columns)):
        raise AttributeError("%s or 'volume' not in columns" %
                             str(prices_cols))

    kline = Kline(name, width=width, height=height)
    kline.add('k-candle',
              df.index.format(),
              df[prices_cols].values.tolist(),
              is_datazoom_show=True,
              datazoom_xaxis_index=[0, 1],
              xaxis_pos=kline_xaxis_pos,
              is_xaxislabel_align=True,
              )

    # volume
    if not 'price_change' in df.columns:
        df['price_change'] = df[prices_cols[1]].diff()
    ups = df.where(df.price_change > 0, 0)['volume']
    downs = df.where(~(df.price_change > 0), 0)['volume']

    bar = Bar()
    bar.add('up',
            x_axis=ups.index.format(),
            y_axis=ups.values.tolist(),
            is_datazoom_show=True,
            legend_top="70%",
            is_stack=True,
            is_xaxislabel_align=True,
            )
    bar.add('down',
            x_axis=downs.index.format(),
            y_axis=downs.values.tolist(),
            is_datazoom_show=True,
            is_stack=True,
            legend_top="70%",
            legend_orient='vertical',
            legend_pos='left',
            yaxis_pos='right',
            is_xaxislabel_align=True,
            # mark_line=["average"],
            )

    # merge
    grid1 = Grid()
    grid1.add(kline, grid_bottom="18%")
    grid1.add(bar, grid_top="75%")

    # add ma
    Line_draw = False
    for ma_ in ma:
        if ma_ in df.columns:
            if Line_draw is False:
                Line_draw = True
                line = Line()
            line.add(ma_, df.index.format(), df[ma_].values.tolist())
    if Line_draw:
        overlap = Overlap()
        overlap.add(grid1)  # overlap kline and ma
        overlap.add(line)

    if render_path:
        overlap.render(render_path)
    return overlap  # .render('k-line.html')

if __name__ == '__main__':
    # 数据导入
    name = '300317'
    period = '1'
    if period.isdigit():
        period += 'day'
    data_raw = data_process.Get_DataFrame(name,'20171210')
    data_raw.sort_index(inplace=True)
    ma5 = create_data.ave_data_create(data_raw.close.values, 5)[:150]
    ma5.reverse()
    ma60 = create_data.ave_data_create(data_raw.close.values, 60)[:150]
    ma60.reverse()
    # 均线维度必须一致，data不能有空值
    data_new = pd.DataFrame(data_raw, columns=['open', 'high', 'low', 'close', 'volume'])
    open = list(data_new.open)[:150]
    open.reverse()
    close = list(data_new.close)[:150]
    close.reverse()
    high = list(data_new.high)[:150]
    high.reverse()
    low = list(data_new.low)[:150]
    low.reverse()
    volume = list(data_new.volume)[:150]
    volume.reverse()
    date = list(data_raw.date)[:150]
    date.reverse()
    data = pd.concat([pd.DataFrame(open, columns=['open']), pd.DataFrame(close, columns=['close']),
                      pd.DataFrame(high, columns=['high']), pd.DataFrame(low, columns=['low']),
                      pd.DataFrame(volume, columns=['volume']), pd.DataFrame(ma5, columns=['ma5']),
                      pd.DataFrame(ma60, columns=['ma60'])], 1)

    data.index = date

    # width = 360, height = 125,
    kline_js('%s_kline_%s' % (name, period),
             data,
             ma=['ma5', 'ma60'],
             width=1800, height=1200,
             render_path='%s_kline_%s.html' % (name, period)
             )
