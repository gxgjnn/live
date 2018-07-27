# coding=utf-8

import re  # 正则表达式
import bs4  # Beautiful Soup 4 解析模块
import urllib2  # 网络访问模块
# import News   #自己定义的新闻结构
import codecs  #解决编码问题的关键 ，使用codecs.open打开文件
import sys   #1解决不同页面编码问题
import numpy as np
import pandas as pd
from snownlp import SnowNLP

reload(sys)                         # 2
sys.setdefaultencoding('utf-8')     # 3


# ##抓取满足条件个股的所有条件新闻并保存，用于情感分析建模
def main_url(stock, period0, period1):
    """
    # 返回的是搜索页面的首页以及所有下一页的列表
    :param stock: 
    :return: 
    """
    stock_basic_list = pd.read_csv('C:/Users/liquan/PycharmProjects/live/stock_basic_list.csv', encoding='utf-8',
                                   dtype={'code': np.str})
    stock_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'name']).split('    ')[1].split('\n')[0]
    # 对字符串进行urlencode
    s = urllib2.quote(stock_name)
    # 选择所有类型，限定日期，限定标题中显示page_box[0].find_all('a')[1]
    url = 'http://search.sina.com.cn/?c=news&q='+s+'&range=title&time=custom&stime='+period0+'&etime='+period1+'&num=20'
    html = urllib2.urlopen(url).read() # .decode('utf8')
    soup = bs4.BeautifulSoup(html, 'html.parser')

    not_exist = soup.find_all('div', attrs={'class': 'tips_01'})
    # 没有按照条件显示的网页内容处理, 也就是搜索按照所有日期搜索的情况发生时，就搜索行业新闻
    if len(not_exist) != 0:
        industry_name = str(stock_basic_list.loc[stock_basic_list.code == stock, 'industry']).split('    ')[1].split('\n')[0]
        s = urllib2.quote(industry_name)
        url = 'http://search.sina.com.cn/?c=news&q=' + s + '&range=title&time=custom&stime=' + period0 + '&etime=' + period1 + '&num=20&col=1_7'
        html = urllib2.urlopen(url).read()
        soup = bs4.BeautifulSoup(html, 'html.parser')
        not_exist = soup.find_all('div', attrs={'class': 'tips_01'})
        if len(not_exist) != 0:
            print '无行业新闻，来打补丁'
    urls = [url]
    # 把该页中的所有下一页合并到一个列表
    page_box = soup.find_all('div', attrs={'class': 'pagebox'})
    if '下一页' in page_box[0].text:
        for i in range(len(page_box[0].find_all('a'))):
            new_url = 'http://search.sina.com.cn' + str(page_box[0].find_all('a')[i]).replace('amp;', '').split('"')[1]
            urls.append(new_url)
            #  = set(urls)
    return set(urls)


def get_news(url,  flag=[]):
    """
    
    :param url: 
    :param flag: 1--positive,0--negative
    :return: 
    """
    global NewsCount
    try:
        html = urllib2.urlopen(url).read()  # .decode('utf8')

        # 解析
        soup = bs4.BeautifulSoup(html, 'html.parser')
        # pattern = 'http://\w+\.baijia\.baidu\.com/article/\w+'  # 链接匹配规则
        links = soup.find_all('div', attrs={'class': 'box-result clearfix'})

        period_content = []
        # 获取URL
        for link in links:
            url_in_url = link.find_all('a')
            date = str(link.find_all('span')).split(' ')[-2]
            url_in_url = str(url_in_url).split('"')[1]
            html = urllib2.urlopen(url_in_url).read()
            soup = bs4.BeautifulSoup(html, 'html.parser')

            title = title[0].text
            title = soup.find_all('h1', attrs={'class': 'main-title'})
            if '表态' in title or '什么' in title or '？' in title or '?' in title or '@' in title or '“' in title or '《'in title or '！'in title or '!' in title or len(title) < 10 :
                continue
            content = soup.find_all('div', attrs={'class': 'article'})
            start_phrase = ''
            for i in range(len(content[0].find_all('p'))):
                phrase = content[0].find_all('p')[i].text
                if '责任编辑' in phrase:
                    phrase = ''
                start_phrase += phrase

            if flag:
                if '：' in title or ':' in title or '部' in title or len(start_phrase) > 1200:
                    file.write(date + '\t' + str(flag) + '\t' + title + '\n')
                else:
                    file.write(date + '\t' + str(flag) + '\t' + title + '\n')
                    file.write(date + '\t' + str(flag) + '\t' + title + start_phrase + '\n')

            period_content.append(start_phrase)
            NewsCount += 1
    except Exception as e:
        print(e)

    return period_content, NewsCount


if __name__ == '__main__':
    stock_id = '000001'
    start = '2018-03-01'
    end = '2018-03-06'
    urls = main_url(stock=stock_id, period0=start, period1=end)

    # url_set = set()  # url集合
    # url_old = set()  # 爬过的url集合

    NewsCount = 0
    contents = []

    # home = 'http://baijia.baidu.com/'  # 起始位置
    # get_all_url(home, period)
    context = "C:\\Users\\liquan\\PycharmProjects\\live\\nlp\\data\\%s.txt" % stock_id
    file = codecs.open(context, "a+")  # 文件操作
    flag = 1
    for url in urls:
        period_content, NewsCount = get_news(url=url, flag=flag)
        # 如果flag=0，最后得到的是查到的近三个月的新闻数据
        if not flag:
            contents.extend(period_content)
    print NewsCount
    file.close()
