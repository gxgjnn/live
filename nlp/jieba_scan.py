# encoding=utf-8
import jieba
import re
from os import path
from sklearn.cross_validation import train_test_split
# import gensim
import numpy as np
# import importlib, sys
# importlib.reload(sys)
# sys.setdefaultencoding('utf8')


# 关于标点符号的处理方式问题
class Scan(object):
    def __init__(self):
        self.path = path
        # pass

    def scan(self, f):
        # 加载自定义库
        # jieba.load_userdict("userdict.txt")

        r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        try:
            f = open(self.path, "r", encoding='UTF-8')
        except Exception as err:
            print(err)
        finally:
            print("文件读取结束")
        outline_1 = []
        i = 0
        count = 0
        for line in f:
            rr = ""
            try:
                rr = line.decode("UTF-8")
            except:
                print("charactor code error UTF-8")
                pass
            if rr == "":
                try:
                    rr = line.decode("GBK")
                except:
                    print("charactor code error GBK")
                    pass
            line = line.strip()
            line = re.sub(r, '', line)

            l_ar = line.split("\t")
            if len(l_ar) != 4:
                continue

            content = l_ar[1]
# ********************
            # id = l_ar[0]
            # title = l_ar[1]
            # content = l_ar[2]
            # label = l_ar[3]

            # seg_title = jieba.cut(title.replace("\t", " ").replace("\n", " "))
            # seg_content = jieba.cut(content.replace("\t", " ").replace("\n", " "))
            # outline = " ".join(seg_title) + "\t" + " ".join(seg_content)

            # 去停用词1
            # liststr = "/ ".join(outline)
            # f_stop = open(stopwords_path)
            # try:
            #     f_stop_text = f_stop.read()
            #     f_stop_text = unicode(f_stop_text, 'utf-8')
            # finally:
            #     f_stop.close()
            # f_stop_seg_list = f_stop_text.split('\n')
            # for word in liststr.split('/'):
            #     if not (word.strip() in f_stop_seg_list) and len(word.strip()) > 1:
            #         outline_1.append(word)
            # 去停用词2
            # stoplist = {}.fromkeys([line.strip() for line in open("../../file/stopword.txt")])
            # segs = [word.encode('utf-8') for word in list(segs)]
            # segs = [word for word in list(segs) if word not in stoplist]

            # outline_2 = "\t__label__" + label + outline_1 + "\t"
            # outf.write(outline_2)
# ******************************
            outline_1 = jieba.cut(line.replace("\t", " ").replace("\n", " "))
            outline_2 = "\t" + outline_1 + "\t"
            outline_1.append(outline_2)
            outf.write(outline_2)

            if i % 2500 == 0:
                count = count + 1
                sys.stdout.flush()
                sys.stdout.write("#")
            i = i + 1
            # del liststr

        f.close()
        outf.close()
        print("\nWord segmentation complete.")
        print(i)
        return outline_2

    def scan_word(self, line):
        # 加载自定义库
        # jieba.load_userdict("userdict.txt")

        r = '[’!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~]+'
        rr = ""
        try:
            rr = line.decode("UTF-8")
        except:
            print("charactor code error UTF-8")
            pass
        if rr == "":
            try:
                rr = line.decode("GBK")
            except:
                print("charactor code error GBK")
                pass
        line = line.strip()
        line = re.sub(r, '', line)
        outline_1 = jieba.cut(line.replace("\t", " ").replace("\n", " "))

        return list(outline_1)


if __name__ == '__main__':
    d = path.dirname(__file__)
    stopwords_path = 'C:\\Users\liquan\PycharmProjects\live\\nlp\snownlp\\normal\stopwords.txt'  # 停用词词表

    text_path = 'txt/lz.txt'  # 设置要分析的文本路径
    text = open(path.join(d, text_path)).read()

    outf = open("lab3fenci.csv", 'w')



