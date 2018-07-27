# coding=utf-8

import re  # 正则表达式
import bs4  # Beautiful Soup 4 解析模块
import urllib2  # 网络访问模块
# import News   #自己定义的新闻结构
import codecs  # 解决编码问题的关键 ，使用codecs.open打开文件
import sys  # 1解决不同页面编码问题
import requests
import numpy as np
import pandas as pd
# from snownlp import SnowNLP
import scrapy
from scrapy.http import Request
from selenium import webdriver
import os
import time
import requests
import datetime
import tushare as ts
import cookielib
reload(sys)  # 2■
sys.setdefaultencoding('utf-8')  # 3

# session = requests.session()
# https://zhuanlan.zhihu.com/p/27115580
# https://blog.csdn.net/trisyp/article/details/78688106


def main_url():
    """
    ### 用于爬去新浪新闻，没有做限制，用于个股文本建模的分类
    :return: 
    """
    global j
    # 取8000页，8万的新闻,两年左右
    for i in range(9925, 10000):
        # print i
        titles = []
        contents = []
        news_time = []
        titles_0 = []
        news_time_0 = []
        contents_0 = []
        timestamp = int(time.time())
        url = 'http://feed.mix.sina.com.cn/api/roll/get?pageid=155&lid=1686&num=10&page=' + str(
            i) + '&callback=feedCardJsonpCallback&_=' + str(timestamp)
        # url = 'http://feed.mix.sina.com.cn/api/roll/get?pageid=155&lid=1686&num=10&page=6360&callback=feedCardJsonpCallback&_=' + str(timestamp)
        # url = 'http://feed.mix.sina.com.cn/api/roll/get?pageid=155&lid=1686&num=10&page=6364&callback=feedCardJsonpCallback&_=1523411566'
        # print url
        html = urllib2.urlopen(url).read()  # .decode('utf8')
        soup = bs4.BeautifulSoup(html, 'html.parser')
        content = soup.text.decode('unicode_escape')
        # file=open('D:\\test0404.txt', 'w')
        # file.write(content)
        titles.extend(re.findall('"title":"(.*?)"', content))
        [titles.remove(x) for x in titles if '\\'in x]
        [titles.remove(x) for x in titles if '\\'in x]
        [titles.remove(x) for x in titles if '\\'in x]
        [titles.remove(x) for x in titles if '\\'in x]
        [titles.remove(x) for x in titles if '\\'in x]
        urls = re.findall('"urls":"(.*?)",', content)
        dates = re.findall('"ctime":"(.*?)"', content)
        for date in dates:
            timeArray = time.localtime(float(date))
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            news_time.append(otherStyleTime)
            news_time_0.append(otherStyleTime)
        # 找正文
        for link in urls:
            try:
                url_in_url = link.replace('\\', '')[2:-2]
                html = urllib2.urlopen(url_in_url).read()
                soup = bs4.BeautifulSoup(html, 'html.parser')
                # 查找正文
                content = soup.find_all('div', attrs={'class': 'article'})
                start_phrase = ''
                try:
                    for i in range(len(content[0].find_all('p'))):
                        phrase = content[0].find_all('p')[i].text.strip()
                        if '责任编辑' in phrase:
                            phrase = ''
                        start_phrase += phrase
                    contents.append(start_phrase)
                except Exception, e:
                    print e
                    contents.append('')
            except Exception, e:
                print e
                contents.append('')
                continue

        titles_0.extend(titles)
        # news_time_0.extend(news_time)
        contents_0.extend(contents)
        for title in set(titles):
            if '表态' in title or '什么' in title or '？' in title or '?' in title or '@' in title or '“' in title or '《'in title or '！'in title or '!' in title or len(title) < 10 :
                i = titles.index(title)
                titles_0.remove(title)
                news_time_0.remove(news_time[i])
                contents_0.remove(contents[i])

        if len(titles_0) == 0:
            continue
        if len(titles_0) != len(contents_0) or len(titles_0) != len(news_time_0):
            continue

        for i in list(range(0, len(titles_0))):
            if '：' in titles_0[i] or ':' in titles_0[i] or '部' in titles_0[i] or len(contents_0[i]) > 1200:
                if '应' in titles_0[i] or '应该' in titles_0[i] or '或' in titles_0[i] or  '若' in titles_0[i] \
                        or '将' in titles_0[i] or '可能' in titles_0[i] or '认识' in titles_0[i] or\
                                '探索' in titles_0[i] or '坚决' in titles_0[i] or '坚决' in titles_0[i] or '要' in titles_0[i] or '恐' in titles_0[ i]:
                    file.write(','.join((news_time_0[i], '1'+titles_0[i])) + '\n')
                else:
                    file.write(','.join((news_time_0[i], titles_0[i])) + '\n')
            else:
                if '应' in titles_0[i] or '应该' in titles_0[i] or '或' in titles_0[i] or '若' in titles_0[i] or \
                                '将' in titles_0[i] or '可能' in titles_0[i] or '认识' in titles_0[i] or \
                                '探索' in titles_0[i] or '坚决'in titles_0[i] or '坚决'in titles_0[i] or  '要' in titles_0[i] or '恐'in titles_0[i]:
                    file.write(','.join((news_time_0[i], '1'+titles_0[i])) + '\n')
                    file.write(','.join((news_time_0[i], '1'+contents_0[i])) + '\n')
                else:
                    file.write(','.join((news_time_0[i], titles_0[i])) + '\n')
                    file.write(','.join((news_time_0[i], contents_0[i])) + '\n')
            j += 1
            end = datetime.datetime.now()
            seconds_diff = (end - start).seconds
            minutes_diff = round(seconds_diff / 60, 1)
            print 'spend:', minutes_diff
            print j
            print news_time_0[i]
            print titles_0[i]


def xue_qiu():
    """
    ###用于爬取雪球的涨跌原因的文章， 建pos,neg语料库
    :return: 
    """
    global j
    contents = []
    chromedriver = "C:/Program Files (x86)/Google/Chrome/Application/chromedriver"
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)  # 模拟打开浏览器
    for i in range(1, 101):
        print 'i:', i
        # 每次更换url都要换cookies
        # 涨停揭秘
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=user&q=%E6%B6%A8%E5%81%9C%E8%82%A1%E6%8F%AD%E7%A7%98&count=20&page='+ str(i)
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=news&q=%E6%B6%A8%E5%81%9C%E8%82%A1%E6%8F%AD%E7%A7%98&count=20&page='+ str(i)
        # 涨原因
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=&q=%E6%B6%A8%E5%8E%9F%E5%9B%A0&count=20' \
        #       '&page=' + str(i)
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=news&q=%E6%B6%A8%E5%8E%9F%E5%9B%A0&count=20' \
        #       '&page=' + str(i)
        # 跌原因
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=user&q=%E8%B7%8C%E5%8E%9F%E5%9B%A0&count=10&' \
        #       '&page=' + str(i)
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=news&q=%E8%B7%8C%E5%8E%9F%E5%9B%A0&count=10&' \
        #       '&page=' + str(i)
        # 晚间利空公告
        # url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=user&q=%E6%99%9A%E9%97%B4%E5%88%A9%E7%A9%BA%E5%85%AC%E5%91%8A&count=20&page='+ str(i)
        url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=news&q=%E6%99%9A%E9%97%B4%E5%88%A9%E7%A9%BA%E5%85%AC%E5%91%8A&count=20&page='+ str(i)
        print url
        # user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
        # user_agent1 = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:49.0) Gecko/20100101 Firefox/49.0"
        user_agent2 = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.87 Safari/537.36"
        # headers = {'User-Agent': user_agent}
        # headers1 = {'User-Agent': user_agent1}
        headers = {'Host': 'xueqiu.com',
                   'Referer': 'https://xueqiu.com/k?q=%E6%99%9A%E9%97%B4%E5%88%A9%E7%A9%BA%E5%85%AC%E5%91%8A',
                   'Origin': 'https://xueqiu.com',
                   'User-Agent': user_agent2,
                   'Cookie': 'aliyungf_tc=AQAAAO/yoDwnWQQAol33Os9vzgZhPbZU; __utmc=1; device_id=d0677bf81f1c588bdd59ea8a6f83f1da; s=fj11r7490d; Hm_lvt_1db88642e346389874251b5a1eded6e3=1523607530,1523936002; __utmz=1.1523936002.7.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; xq_a_token=0d524219cf0dd2d0a4d48f15e36f37ef9ebcbee1; xq_a_token.sig=P0rdE1K6FJmvC2XfH5vucrIHsnw; xq_r_token=7095ce0c820e0a53c304a6ead234a6c6eca38488; xq_r_token.sig=xBQzKLc4EP4eZvezKxqxXNtB7K0; u=391524564970264; __utma=1.1888615952.1523607530.1524570685.1524708901.13; __utmt=1; __utmb=1.19.10.1524708901; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1524713474',
                   'Connection': 'keep-alive'}
        html = requests.get(url, headers=headers).text
        # print html
        results = re.findall('"target":"(.*?)"', html)
        head = 'https://xueqiu.com'
        for result in results:
            ulr = head + result
            print ulr
            try:
                # 模拟浏览器
                driver.get(ulr)
                phrases = driver.find_element_by_class_name('article__bd__detail')
                title = driver.find_element_by_class_name('article__bd__title')
                title = str(title.text).replace('\n', '')
                new_phrases = str(phrases.text).replace('\n', '')
                file.write(title + '\t' + new_phrases + '\n')
                # contents.append(new_phrases)
            except(Exception):
                print('*' * 50)
                print(Exception)
                print('*' * 50)
                new_phrases = str(phrases.text).replace('\n', '')
                file.write('No Title' + '\t' + new_phrases + '\n')
                # time.sleep(20)
                # continue
            j += 1
            print 'j', j
            # time.sleep(2)

        # end = datetime.datetime.now()
        # secondsDiff = (end - start).seconds
        # minutesDiff = round(secondsDiff / 60, 1)
        # print 'cost:', minutesDiff


def east_fortune_1(stock_id):
    """
    ###爬取东方财富个股业绩预告明细， 用于cnn模型一级过滤
    :return: string
    """
    url = 'http://data.eastmoney.com/bbsj/' + str(stock_id) + '.html'
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response, 'html.parser')
    res = soup.find_all('div', attrs={'class': 'contentBox'})
    title = str(res[4].find_all('div', attrs={'class': 'tit'})[0].text).strip()
    if '业绩预告' in title:
        latest_news = str(res[4].find_all('div', attrs={'class': 'content'})[0].text).split('\r\n')[-1].strip()
        # 取离现在最近的业绩预告
        latest_new = latest_news.split('。')[0]
        report_date = latest_new[:10]
        report_date = datetime.datetime(int(report_date[0:4]), int(report_date[5:7]), int(report_date[8:10]))
        current_date = datetime.datetime.now()
        if current_date <= report_date:
            new = latest_new[10:]
        else:
            new = '业绩预报尚未发表'
    else:
        new = '业绩预报尚未发表'
    return new


def east_fortune_2(stock_id):
    """
    ###爬取东方财富个股新闻（只看近30天内的）， 用于cnn模型二级过滤
    :return: 包含新闻的list
    """
    url = 'http://guba.eastmoney.com/list,' + str(stock_id) + ',1,f.html'
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response, 'html.parser')
    contents = soup.find_all('span', attrs={'class': 'l3'})
    dates = soup.find_all('span', attrs={'class': 'l6'})

    current_date = time.strftime("%Y%m%d")
    date_line = getday(int(current_date[0:4]), int(current_date[4:6]), int(current_date[6:8]), -30)
    date_line = datetime.datetime.strptime(date_line, '%Y-%m-%d')
    j = 0
    for i in range(1, len(dates)):
        date = str(dates[i].text.strip())
        date = datetime.datetime(int(current_date[0:4]), int(date[0:2]), int(date[3:5]))
        if date >= date_line:
            j += 1
        else:
            break

    news_box = []
    for k in range(1, j):
        new = re.findall('"(.*?)"', str(contents[k]))[-1]
        if '融资融券信息' not in new:
            if '日' not in new.decode('utf-8')[-5]:
                news_box.append(new)

    return news_box


def east_fortune_3(stock_id):
    """
    ###爬去东方财富行业数据，因为语料库的限制，这部分等以后语料库丰富了在做
    :param stock_id: sh/sz.....
    :return: 
    """
    if stock_id[0] == '6':
        stock_id = 'sh' + stock_id
    else:
        stock_id = 'sz' + stock_id
    url = 'http://emweb.securities.eastmoney.com/IndustryAnalysis/Index?type=web&code=' + str(stock_id) + '#'
    response = requests.get(url).text
    soup = bs4.BeautifulSoup(response, 'html.parser')
    contents = soup.find_all('span', attrs={'class': 'l3'})


def east_fortune_4(stock_id):
    """
    ###如果前两级过滤结果是既没有业绩预告，也没有近期相关新闻，就看基本财务信息。
    爬去东方财富个股财报分析中的三个指标
     :param stock_id: sh/sz.....
    :return: str
    """
    if stock_id[0] == '6':
        stock_id = 'sh' + stock_id
    else:
        stock_id = 'sz' + stock_id
    url = 'http://emweb.securities.eastmoney.com/NewFinanceAnalysis/MainTargetAjax?ctype=4&type=0&code=' + str(stock_id)
    user_agent2 = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    headers = {'Host': 'emweb.securities.eastmoney.com',
               'User-Agent': user_agent2,
               'Cookie': 'st_pvi=19781585008501; em_hq_fls=js; emhqfavor=; pgv_pvi=9007962112; _qddaz=QD.ag5x00.maeneb.jfapoli9; qgqp_b_id=171ee30385403f46befcde96415ec914; HAList=a-sz-000002-%u4E07%u79D1A%2Ca-sz-000001-%u5E73%u5B89%u94F6%u884C%2Cf-0-000001-%u4E0A%u8BC1%u6307%u6570%2Cf-0-399001-%u6DF1%u8BC1%u6210%u6307%2Ca-sz-002310-%u4E1C%u65B9%u56ED%u6797; emshistory=%5B%22%E8%A1%8C%E4%B8%9A%E7%A0%94%E6%8A%A5%22%2C%22885783%22%2C%22000001%22%2C%22000001%202017-03-27%22%2C%22399001%20(%E6%B7%B1%E8%AF%81%E6%88%90%E6%8C%87)%22%2C%22399001%20(%E6%B7%B1%E8%AF%81%E6%88%90%E6%8C%87)2018.03.27%E8%B5%B0%E5%8A%BF%E5%88%86%E6%9E%90%22%2C%22399001%20(%E6%B7%B1%E8%AF%81%E6%88%90%E6%8C%87)%E6%98%A8%E6%97%A5%E8%B5%B0%E5%8A%BF%E5%88%86%E6%9E%90%22%5D; st_si=34006067650823',
               'Connection': 'keep-alive'}
    html = requests.get(url, headers=headers).text
    # print html
    mgjzc_=[]
    mgjzc = re.findall('"mgjzc":"(.*?)"', html)
    mgjzc = [float(i) for i in mgjzc]
    mggjj = re.findall('"mggjj":"(.*?)"', html)
    mggjj = [float(i) for i in mggjj]
    mgwfplr = re.findall('"mgwfply":"(.*?)"', html)
    mgwfplr = [float(i) for i in mgwfplr]

    # 每股净资产的均值要大于每股公积
    m_S = pd.Series(mgjzc)
    lr_S = pd.Series(mgwfplr)
    if m_S.mean() > mggjj[0]:
        # 当前每股净资产要大于均值与中位数
        if (mgjzc[0] >= m_S.mean()) and (mgjzc[0] >= m_S.median()):
            # 每股未分配利润要大于0 ，且当前每股未分配利润要大于均值和中位数，且当前每股未分配利润要大于等于前一个
            if (mgwfplr[0] > 0) and (mgwfplr[0] >= lr_S.mean()) and (mgwfplr[0] >= lr_S.median()):
                stock_basic = '基本面通过'
    else:
        stock_basic = '基本面不通过'
    return stock_basic


def getday(y, m, d, n):
    """
    日期计算
    :param y: 年
    :param m: 月
    :param d: 日
    :param n: 间隔天数
    :return: str
    """
    the_date = datetime.datetime(y, m, d)
    result_date = the_date + datetime.timedelta(days=n)
    d = result_date.strftime('%Y-%m-%d')
    return d


if __name__ == '__main__':
    # import datetime
    # start = datetime.datetime.now()
    # j = 0
    # file = codecs.open('neg.txt', 'a+')
    # xue_qiu()
    # file.close()

    # stock = '002486'
    # stock = '300733'
    # stock = '600680'
    # news_box = east_fortune_2(stock)
    # print news_box
    stock = '600680'
    a= east_fortune_2(stock)
    print(a)


    # import os
    # from multiprocessing import Pool
    # # king('20161230', '20170126')
    # start = datetime.datetime.now()
    # print 'Parent process %s.' % os.getpid()
    # p = Pool(2)
    # p.apply_async(king, args=('20161230', '20170103'))
    #
    # print 'Waiting for all subprocesses done...'
    # p.close()
    # p.join()
    # print 'All subprocesses done.'
    #
    # end = datetime.datetime.now()
    # secondsDiff = (end - start).seconds
    # minutesDiff = round(secondsDiff / 60, 1)
    # print 'multi_process_9_minutesDiff', minutesDiff
