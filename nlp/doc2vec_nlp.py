# encoding=utf-8

from jieba_scan import *


# 读取并预处理数据
def get_dataset():
    # # 读取数据
    # with open('C:\\Users\\liquan\\PycharmProjects\\live\\nlp\\pos_file.txt','r') as infile:
    #     text_data = infile.readlines()
    with open(path, 'r') as infile:
        y = infile.readlines()
    # 清洗所有中文
    obj = Scan(path)
    text_data = obj.scan()
    # 将数据分割为训练与测试集
    x_train, x_test, y_train, y_test = train_test_split(text_data, y, test_size=0.2)

    x_train = labelizeReviews(x_train, 'TRAIN')
    x_test = labelizeReviews(x_test, 'TEST')

    return x_train, x_test, y_train, y_test


LabeledSentence = gensim.models.doc2vec.LabeledSentence


def labelizeReviews(reviews, label_type):
    labelized = []
    for i,  v in enumerate(reviews):
        label = '%s_%s'%(label_type,i)
        labelized.append(LabeledSentence(v, [label]))
    return labelized


# #读取向量
def getVecs(model, corpus, size):
    vecs = [np.array(model.docvecs[z.tags[0]]).reshape((1, size)) for z in corpus]
    return np.concatenate(vecs)


# #对数据进行训练
def train(x_train, x_test, size=400, epoch_num=10):
    # 实例DM和DBOW模型
    # Distributed Memory(DM) 和 Distributed Bag of Words(DBOW)。DM 试图在给定上下文和段落向量的情况下预测单词的概率。
    # 在一个句子或者文档的训练过程中，段落 ID 保持不变，共享着同一个段落向量。DBOW 则在仅给定段落向量的情况下预测段落中一组随机单词的概率。
    # model_dm = Doc2Vec(min_count=1, window=10, size=size, sample=1e-3, negative=5, workers=3)
    # model_dbow = Doc2Vec(min_count=1, window=10, size=size, sample=1e-3, negative=5, dm=0, workers=3)

    x_train_0 = x_train
    x_test_0 = x_test
    # # new_train = df(np.concatenate((x_train, x_test, unsup_reviews)), 500)
    # # 使用所有的数据建立词典
    x_train_0[len(x_train_0):len(x_train_0)] = x_test_0
    # x_train_0[len(x_train_0):len(x_train_0)] = unsup_reviews
    model_dm = gensim.models.doc2vec.Doc2Vec(x_train_0, min_count=1, window=10, size=size, sample=1e-3, negative=5, workers=3)
    model_dbow = gensim.models.doc2vec.Doc2Vec(x_train_0, min_count=1, window=10, size=size, sample=1e-3, negative=5, dm=0, workers=3)

    # model_dm.build_vocab(x_train_0)
    # model_dbow.build_vocab(x_train_0)
    # model_dm.build_vocab(np.concatenate((x_train, x_test, unsup_reviews)))
    # model_dbow.build_vocab(np.concatenate((x_train, x_test, unsup_reviews)))
    # model_dm.build_vocab(x_train)
    # model_dbow.build_vocab(x_train)

    # 进行多次重复训练，每一次都需要对训练数据重新打乱，以提高精度
    # all_train_reviews = np.concatenate((x_train, unsup_reviews))
    # all_train_reviews = np.array(x_train)
    # for epoch in range(epoch_num):
    #     perm = np.random.permutation(all_train_reviews.shape[0])
    #     model_dm.train(all_train_reviews[perm],total_examples=model_dm.corpus_count, epochs=model_dm.epochs)
    #     model_dbow.train(all_train_reviews[perm],total_examples=model_dbow.corpus_count, epochs=model_dbow.epochs)
    # for epoch in range(10):
    #     model_dm.train(x_train)
    #     model_dm.alpha -= 0.002  # decrease the learning rate
    #     model_dm.min_alpha = model_dm.alpha  # fix the learning rate, no deca
    #     model_dm.train(x_train)
    #     model_dbow.train(x_train)
    #     model_dbow.alpha -= 0.002  # decrease the learning rate
    #     model_dbow.min_alpha = model_dbow.alpha  # fix the learning rate, no deca
    #     model_dbow.train(x_train)

    x_train, x_test, unsup_reviews, y_train, y_test = get_dataset()

    # 将训练完成的数据转换为vectors
    # 获取训练数据集的文档向量
    train_vecs_dm = getVecs(model_dm, x_train, size)
    train_vecs_dbow = getVecs(model_dbow, x_train, size)
    train_vecs = np.hstack((train_vecs_dm, train_vecs_dbow))

    from random import shuffle
    # 训练测试数据集
    # x_test = np.array(x_test)
    for epoch in range(epoch_num):
        model_dm.train(shuffle(x_test))
        # perm = np.random.permutation(x_test.shape[0])
        # model_dm.train(x_test[perm],total_examples=75000, epochs=model_dm.epochs)
        # model_dbow.train(x_test[perm],total_examples=model_dbow.corpus_count, epochs=model_dbow.epochs)

    # 获取测试数据集的文档向量
    test_vecs_dm = getVecs(model_dm, x_test, size)
    test_vecs_dbow = getVecs(model_dbow, x_test, size)
    test_vecs = np.hstack((test_vecs_dm, test_vecs_dbow))

    return model_dm, model_dbow, train_vecs, test_vecs



