# -*- coding: utf-8 -*-

# 一个简单例子---中国图书网
# 爬虫
# 正则表达式爬虫
import requests
import re




url = 'http://www.bookschina.com/book_find2/?stp=python'
content = requests.get(url).text
title = re.findall('jpg" title="(.*?)"', content)
author = re.findall('作者：.*?;sbook=(.*?)">.*?出版社：', content)
pubhouses = re.findall('出版社：.*?">(.*?)</a><br>出版时间：', content)
pubtime = re.findall('</a><br>出版时间：(.*?) <br>ISBN：', content)
ISBN = re.findall('<br>ISBN：(.*?)<br>原价：', content)
raw_price = re.findall('ISBN：.*?<br>原价：￥(.*?)<br>现价：', content)
now_price = re.findall('现价：￥<span class="red12">(.*?)</span>&nbsp;&nbsp;&nbsp;&nbsp;您节省：', content)
jiesheng = re.findall('您节省：<span class="red12">￥(.*?)</span>', content)
discount = re.findall('您节省：<span class="red12">.*?</span>&nbsp;&nbsp;&nbsp;&nbsp;（(.*?)折）<br>', content)

file = open('books.csv', 'w')
for i in list(range(0, len(title))):
    file.write(','.join((
                        title[i], author[i], pubhouses[i], pubtime[i], ISBN[i], raw_price[i], now_price[i], jiesheng[i],
                        discount[i])) + '\n')
    # print(title[i],author[i],pubhouses[i],pubtime[i],ISBN[i],raw_price[i],now_price[i],jiesheng[i],discount[i])
file.close()

# BeautifulSoup方法
import requests
from bs4 import BeautifulSoup

url = 'http://www.bookschina.com/book_find2/?stp=python'
response = requests.get(url).text

soup = BeautifulSoup(response, 'html.parser')

res = soup.find_all('div', attrs={'class': 'wordContent'})
for i in res:
    title = i.find_all('a')[0].text
    author = i.find_all('a')[1].text
    pubhouse = i.find_all('a')[2].text
    text = i.find_all('br')[2].text
    pubtime = text[text.find('：') + 1:text.find('ISBN：') - 1]
    ISBN = text[text.find('ISBN：') + 6: text.find('原价：￥')]
    raw_price = text[text.find('原价：￥') + 4: text.find('现价')]
    now_price = text[text.find('现价') + 4: text.find('现价') + 9]
    diff = text[text.find('您节省：') + 5: text.find('您节省：') + 9]
    discounts = text[-4:-1]
    print(title, author, pubhouse, pubtime, ISBN, raw_price, now_price, diff, discounts)

# 写入txt文档
import requests
from bs4 import BeautifulSoup

url = 'http://www.bookschina.com/book_find2/?stp=python'
response = requests.get(url).text

soup = BeautifulSoup(response, 'html.parser')

res = soup.find_all('div', attrs={'class': 'wordContent'})
file = open('Chinese Lib Net.txt', 'w', encoding='utf-8')
for i in res:
    title = i.find_all('a')[0].text
    author = i.find_all('a')[1].text
    pubhouse = i.find_all('a')[2].text
    text = i.find_all('br')[2].text
    pubtime = text[text.find('：') + 1:text.find('ISBN：') - 1]
    ISBN = text[text.find('ISBN：') + 6: text.find('原价：￥')]
    raw_price = text[text.find('原价：￥') + 4: text.find('现价')]
    now_price = text[text.find('现价') + 4: text.find('现价') + 9]
    diff = text[text.find('您节省：') + 5: text.find('您节省：') + 9]
    discounts = text[-4:-1]
    file.write('\t'.join((title, author, pubhouse, pubtime, ISBN, raw_price, now_price, diff, discounts)) + '\n')
    print(title, author, pubhouse, pubtime, ISBN, raw_price, now_price, diff, discounts)
file.close()

# 写入数据库
# DROP TABLE IF EXISTS books ;
# CREATE TABLE books(
# title VARCHAR(50),
# author VARCHAR(50),
# pubhouse VARCHAR(20),
# pubtime VARCHAR(20),
# ISBN VARCHAR(20),
# raw_price VARCHAR(10),
# now_price VARCHAR(10),
# diff VARCHAR(10),
# discounts VARCHAR(10)
# );
#
#
# SELECT * FROM books;


import requests, pymysql
from bs4 import BeautifulSoup

s1 = 'http://www.bookschina.com/book_find2/default.aspx?pageIndex='
s2 = '&stp=python&dmethod=all&sType=0'
urls = []
for i in list(range(1, 7)):
    urls.append(s1 + str(i) + s2)

for url in urls:
    response = requests.get(url).text
    soup = BeautifulSoup(response, 'html.parser')
    res = soup.find_all('div', attrs={'class': 'wordContent'})

    for i in res:
        title = i.find_all('a')[0].text
        author = i.find_all('a')[1].text
        pubhouse = i.find_all('a')[2].text
        text = i.find_all('br')[2].text
        pubtime = text[text.find('：') + 1:text.find('ISBN：') - 1]
        ISBN = text[text.find('ISBN：') + 6: text.find('原价：￥')]
        raw_price = text[text.find('原价：￥') + 4: text.find('现价')]
        now_price = text[text.find('现价') + 4: text.find('现价') + 9]
        diff = text[text.find('您节省：') + 5: text.find('您节省：') + 9]
        discounts = text[-4:-1]
        print(title, author, pubhouse, pubtime, ISBN, raw_price, now_price, diff, discounts)
        # 创建连接
        connect = pymysql.connect(host='localhost', user='root', password='snake', port=3306, database='rmysql',
                                  charset='utf8')

        cursor = connect.cursor()
        sql = '''insert into books(title,author,pubhouse,pubtime,ISBN,raw_price,now_price,diff,discounts) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        cursor.execute(sql, (title, author, pubhouse, pubtime, ISBN, raw_price, now_price, diff, discounts))
        connect.commit()
        cursor.close()
        connect.close()