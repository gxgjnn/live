# encoding=utf-8

from jieba_scan import *
import fasttext

# 词向量模型学习
# Skipgram model
model = fasttext.skipgram('data.txt', 'model')
print model.words # list of words in dictionary

# CBOW model
model = fasttext.cbow('data.txt', 'model')
print model.words # list of words in dictionary

# 文本分类
classifier = fasttext.supervised('data.train.txt', 'model')

# 创建一个简单的模型
classifier = fasttext.supervised("lab3fenci.csv","lab3fenci.model",label_prefix="__label__")
# 对模型进行测试，观察其精度
result = classifier.test("lab3fenci.csv")
print result.precision
print result.recall
# 继续训练
classifier = fasttext.supervised("lab3fenci.csv","lab3fenci.model",label_prefix="__label__",lr=0.1,epoch=100,dim=200,bucket=5000000)
result = classifier.test("lab3fenci.csv")
print result.precision
print result.recall
#############################################################
# load训练好的模型
classifier = fasttext.load_model('lab3fenci.model.bin', label_prefix='__label__')
result = classifier.test('.txt')
print result.precision
print result.recall

# 预测
texts = ['example very long text 1', 'example very longtext 2']
labels = classifier.predict(texts)
print labels

# Or with the probability
labels = classifier.predict_proba(texts)
print labels