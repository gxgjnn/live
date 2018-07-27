# -*- coding: utf-8 -*-
# 导入所需的开发模块
import requests
import re
from snownlp import SnowNLP

# 创建snownlp对象，设置要测试的语句
s = SnowNLP(u'这东西不错。。')
# 调用sentiments方法获取积极情感概率
x = s.sentiments

if __name__ == '__main__':
    print x