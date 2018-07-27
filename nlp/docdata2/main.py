__author__ = "lybroman@hotmail.com"

import gensim, smart_open
from sklearn.cross_validation import train_test_split
import sklearn.linear_model as lm
import numpy as np
from sklearn.externals import joblib
import datetime

# here we select the lowest-score samples and highest-score samples
# our goal is to train a model which could tell good comments from bad comments

sources_train = {'C:\\Users\\liquan\\PycharmProjects\\live\\nlp\\cnndata\\1_train.txt':'ONE', 'C:\\Users\\liquan\\PycharmProjects\\live\\nlp\\cnndata\\5_train.txt':'FIVE'}


def read_corpus(source_set):
    ct = 0
    for source_file, prefix in source_set.items():
        with smart_open.smart_open(source_file, encoding="utf-8") as f:
            for i, line in enumerate(f):
                # split with space to isolate each word
                # the words list are tagged with a label as its identity
                yield gensim.models.doc2vec.TaggedDocument(gensim.utils.to_unicode(line).split(), [prefix + '_%s' % i])

# 0. load tagged corpus
train_corpus = list(read_corpus(sources_train))
# print(train_corpus[0])


# 1. create the Doc2Vec model
# you need to adjust the hyper-parameters, e.g. size and iter
model = gensim.models.doc2vec.Doc2Vec(vector_size=150, min_count=1, epochs=50, workers=7)

# 2. build vocabulary
model.build_vocab(train_corpus)

start = datetime.datetime.now()
# 3. train the model
for epoch in range(5):
    # if you wanna to have more epoch you'd better shuffle the train_corpus
    model.train(train_corpus, total_examples=model.corpus_count, epochs=model.iter)
end = datetime.datetime.now()
seconds_diff = (end - start).seconds
minutes_diff = round(seconds_diff / 60, 1)
print 'create_box_minutes_diff', minutes_diff

# save you model if you wanna to reload directly next time
model.save('./my_db1.d2v')
# e.g. model = gensim.Doc2Vec.load('./my_db.d2v')

# 4. train classifier
# 4.1 prepare labelled data, num of score 1 and num of score 5
num_1 = 2910
num_5 = 5882
total = num_1 + num_5

# size is 150 in previous step1
train_arrays = np.zeros((total, 150))
train_labels = np.zeros(total)

for i in range(total):
    if i < num_1:
        prefix_train_pos = 'ONE_' + str(i)
        train_arrays[i] = model.docvecs[prefix_train_pos]
        train_labels[i] = 0
    elif i < num_1 + num_5:
        prefix_train_pos = 'FIVE_' + str(i - num_1)
        train_arrays[i] = model.docvecs[prefix_train_pos]
        train_labels[i] = 1

# use test_size * total as test data to validate the classifier
# use (1 - test_size) as trainnin data for the classifier
train, test, train_label, test_label = train_test_split(
    train_arrays, train_labels, test_size=0.2)

# 4.2 train the LR classifier
classifier = lm.LogisticRegression()
classifier.fit(train, train_label)

# 5 check the score(R^2)
# > 0.6 is reasonable good
print(classifier.score(test, test_label))

# 6 save the classifer for future use
joblib.dump(classifier,'classifier.model')

if __name__ == '__main__':
    # 0. load tagged corpus
    train_corpus = list(read_corpus(sources_train))
    # print(train_corpus[0])
