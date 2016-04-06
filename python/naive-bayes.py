__author__ = 'felipeformentiferreira'

import os
import sys
import glob
import re
import math
import random
from collections import Counter

def filelist(pathspec):

    files_list = []
    for file_i in glob.glob(pathspec):
        file_info = os.stat(file_i)
        if file_info.st_size > 0:
            files_list.append(file_i)
    return files_list

def words(document):

    document.replace("'", " ")
    regex = re.compile('[^a-zA-Z ]')
    text = regex.sub(' ', document)
    wordlist = []
    try:
        text_aux = text.split("critique :")
        text = text_aux[1]
    except:
        text = text_aux[0]

    words = text.split(" ")
    for word in words:
        if len(word) > 2:
            word = word.lower()
            wordlist.append(word)
    return wordlist


def sampling(pos_list, neg_list):

    pos_test = random.sample(pos_list, int(round(len(pos_list)/3.0)))
    neg_test = random.sample(neg_list, int(round(len(neg_list)/3.0)))

    pos_train = [i for i in pos_list if i not in pos_test]
    neg_train = [i for i in neg_list if i not in neg_test]

    # for training
    train_dict = {}
    train_dict['pos'] = pos_train
    train_dict['neg'] = neg_train

    # for testing
    test_list = pos_test + neg_test

    # for accuracy
    pos_dict = dict((el, 'pos') for el in pos_test)
    neg_dict = dict((el, 'neg') for el in neg_test)
    test_dict = pos_dict.copy()
    test_dict.update(neg_dict)

    return train_dict, test_dict, test_list

def training(train_dict):

    doc_classes = ['pos', 'neg']
    pos_len = len(train_dict['pos'])
    neg_len = len(train_dict['neg'])

    prob_class = {}
    prob_class['pos'] = float(pos_len)/(pos_len + neg_len)
    prob_class['neg'] = float(neg_len)/(pos_len + neg_len)

    words_class = {}                            # all words of each class
    words_list = []                             # list of all words
    for doc_class in train_dict:

        documents = train_dict[doc_class]       # List of files for each category (pos/neg)
        words_class_aux = []
        for document in documents:
            filename = open(document)
            text = filename.read()
            filename.close()
            dwords = words(text)
            words_class_aux += dwords
            words_list += dwords
        words_class[doc_class] = words_class_aux

    words_set = set(words_list)                 # Unique set of all words
    Unique_words = len(words_set)
    cond_prob = {}                              # P(w|class)
    for doc_class in doc_classes:
        word_class_list = words_class[doc_class]
        count_words = len(word_class_list)
        words_class_dict = {}
        count_class_words = Counter(word_class_list)
        for word in count_class_words:
            words_class_dict[word] = \
                (1.0 + count_class_words[word]) / (count_words + Unique_words)
        cond_prob[doc_class] = words_class_dict

    return prob_class, cond_prob, count_words, Unique_words

def testing(test_list, prob_class, cond_prob, count_words, Unique_words):

    doc_classes = ['pos', 'neg']
    prediction = {}
    for document in test_list:
        filename = open(document)
        text = filename.read()
        doc_words = words(text)
        highest = - 99999999
        for doc_class in doc_classes:
            prob_val = math.log(prob_class[doc_class])
            cond_prob_aux = cond_prob[doc_class]
            for word in doc_words:
                if word in cond_prob_aux:
                    prob_val += math.log(cond_prob_aux[word])
                else:
                    prob_val += math.log(1/(count_words + Unique_words + 1.0))

            if prob_val > highest:
                highest = prob_val
                prediction[document] = doc_class
    return prediction

def accuracyTest(dict1, dict2):
    acc = 0.0
    total = len(dict1)

    for key in dict1.keys():
        if key in dict2.keys():
            if dict1[key] == dict2[key]:
                acc += 1
    acc /= total
    return acc

def main(my_directory):

    pathspec_pos = my_directory + '/pos/*.txt'
    pathspec_neg = my_directory + '/neg/*.txt'

    pos_list = filelist(pathspec_pos)
    neg_list = filelist(pathspec_neg)

    iterations = 3
    acc = 0.0
    for i in range(iterations):
        print 'Iteration %i' % (i+1)
        # 'SAMPLING'
        train_dict, test_dict, test_list = sampling(pos_list, neg_list)

        # 'TRAINING'
        prob_class, cond_prob, count_words, Unique_words = training(train_dict)

        # 'TESTING'
        prediction = testing(test_list, prob_class, cond_prob, count_words, Unique_words)

        # "ACCURACY"
        aux = accuracyTest(prediction, test_dict)
        acc = acc + aux
        print "accuracy: %f" % (100*aux), "%"

    ave_accuracy = acc/iterations
    print "ave_accuracy: %f" % (100 * ave_accuracy), "%"
    return

#path = sys.argv[2]
path = "----/test_folder"
main(path)