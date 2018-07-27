# coding: utf-8

from __future__ import print_function

import os
import tensorflow as tf
import tensorflow.contrib.keras as kr

from nlp.cnn_rnn.cnn_model import TCNNConfig, TextCNN
from nlp.cnn_rnn.data.cnews_loader import read_vocab, read_category
import numpy as np

try:
    bool(type(unicode))
except NameError:
    unicode = str

base_dir = 'C:\\Users\liquan\PycharmProjects\live\\nlp\\news_collection'
vocab_dir = os.path.join(base_dir, 'news_vocab.txt')

save_dir = 'checkpoints_32_20/textcnn'
save_path = os.path.join(save_dir, 'best_validation.ckpt')  # 最佳验证结果保存路径


class CnnModel:
    def __init__(self):
        self.config = TCNNConfig()
        self.categories, self.cat_to_id = read_category()
        self.words, self.word_to_id = read_vocab(vocab_dir)
        self.config.vocab_size = len(self.words)
        self.model = TextCNN(self.config)

        self.session = tf.Session()
        self.session.run(tf.global_variables_initializer())
        saver = tf.train.Saver()
        saver.restore(sess=self.session, save_path=save_path)  # 读取保存的模型

    def predict(self, message):
        # 支持不论在python2还是python3下训练的模型都可以在2或者3的环境下运行
        content = unicode(message)
        data = [self.word_to_id[x] for x in content if x in self.word_to_id]

        feed_dict = {
            self.model.input_x: kr.preprocessing.sequence.pad_sequences([data], self.config.seq_length),
            self.model.keep_prob: 1.0
        }

        y_pred_cls = self.session.run(self.model.y_pred_cls, feed_dict=feed_dict)
        y_prob = self.session.run(self.model.prob, feed_dict=feed_dict)
        status = list(y_prob[0]).index(max(y_prob[0]))
        prob = max(y_prob[0])
        return self.categories[status], prob


if __name__ == '__main__':
    cnn_model = CnnModel()
    test_demo = ['嘉麟杰预计上半年净利润-3500.00万元至-2000.00']
    # test_demo = ['啥几把玩意我靠']
    for i in test_demo:
        print(cnn_model.predict(i))
