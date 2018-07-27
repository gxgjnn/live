# encoding=utf-8

# this script is especially for Chinese docs,
# for English related docs, just doc.split(' ') is fine~

# using third-party package jieba to
import jieba, os, traceback
from string import maketrans
import sys
import numpy as np
import re
reload(sys)
sys.setdefaultencoding('utf8')

# , encoding='gb2312'
def seg():
    for tag in label:
        # score from 1 -> 5
        for score in range(1, 6):
            with open('C:\Users\liquan\PycharmProjects\live\\nlp\cnndata\{0}_{1}.txt'.format(score, tag), 'w') as f:
                for file in os.listdir('C:\Users\liquan\PycharmProjects\live\\nlp\cnndata\{0}_{1}'.format(score, tag)):
                    try:
                        with open('C:\Users\liquan\PycharmProjects\live\\nlp\cnndata\{0}_{1}\\{2}'.format(score, tag, file), 'r') as ff:
                            # since doc won't be too long, so read all at once
                            line = ff.read()
                            line = line.decode('gb2312')
                            line = str(np.array(line))
                            # line = line.decode('utf-8')
                            # filter some non-related chars
                            line0 = []
                            filter_chars = ['\r', '\n', '\t', '，', '。', '；', '！', ',', '.', ':',  ';', '：', '、', '“', '”', '‘', '’']
                            for i in range(len(filter_chars)):
                                line = line.replace(filter_chars[i], '')
                            # outtab = '                                     '
                            # trantab = maketrans(filter_chars, outtab)
                            # line = line.translate(trantab)
                            # filter_chars = filter_chars.decode("utf8")
                            # trans_dict = dict.fromkeys((ord(_) for _ in filter_chars), '')
                            # line = line.translate(trans_dict)
                            # line = line.strip()
                            # line1 = re.sub(filter_chars, '', line)
                            # words segment
                            it = jieba.cut(line, cut_all=False)
                            _ = []
                            for w in it:
                                _.append(w)

                            f.write(' '.join(_) + '\n')
                    except:
                        # bypass some bad samples for decoding errors
                        # print(traceback.format_exc())
                        # print(f'failed to parse {file}')
                        pass


if __name__ == '__main__':
    label = ['train', 'test']
    seg()
