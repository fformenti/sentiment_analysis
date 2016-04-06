from pyspark import SparkConf,SparkContext
import re
import math

AWS_ACCESS_KEY_ID = "-------"
AWS_SECRET_ACCESS_KEY = "--------"

sc = SparkContext()
sc._jsc.hadoopConfiguration().set("fs.s3n.awsAccessKeyId", AWS_ACCESS_KEY_ID)
sc._jsc.hadoopConfiguration().set("fs.s3n.awsSecretAccessKey", 
    AWS_SECRET_ACCESS_KEY)

#======== Reading Data ======
rdd_train_pos = sc.textFile('s3n://-----.txt')
rdd_train_neg = sc.textFile('s3n://-----.txt')
rdd_test_pos = sc.textFile('s3n://-----.txt')
rdd_test_neg = sc.textFile('s3n://-----.txt')

#======== Training ======
doc_pos_count = rdd_train_pos.count()
doc_neg_count = rdd_train_neg.count()
doc_count = doc_pos_count + doc_neg_count

def parseWord(line):
    words = re.compile(r'\W+', re.UNICODE).split(line)
    return [(word.lower(),1.0) for word in words if len(word) > 1]

def line2list(line):
    words = re.compile(r'\W+', re.UNICODE).split(line)
    return [word.lower() for word in words if len(word) > 1]

words_pos = rdd_train_pos.flatMap(parseWord)
total_words_pos = words_pos.count()
words_pos_count = words_pos.reduceByKey(lambda x,y: x + y)
words_pos_prob = words_pos_count.mapValues(lambda x: x/total_words_pos)

words_neg = rdd_train_neg.flatMap(parseWord)
total_words_neg = words_neg.count()
words_neg_count = words_neg.reduceByKey(lambda x,y: x + y)
words_neg_prob = words_neg_count.mapValues(lambda x: x/total_words_neg)

words_count = words_pos_count.union(words_neg_count).reduceByKey(lambda x,y: x + y)
total_words = total_words_pos + total_words_neg
words_prob = words_count.mapValues(lambda x: x/total_words)

pos_prob = doc_pos_count/float(doc_count)
neg_prob = doc_neg_count/float(doc_count)

words_pos_prob_dict = dict(words_pos_prob.collect())
words_neg_prob_dict = dict(words_neg_prob.collect())
words_prob_dict = dict(words_prob.collect())

#======== Testing ======

def predict(line):
    word_list = line2list(line)
    pred_pos_prob = 0
    pred_neg_prob = 0
    for word in word_list:
        try:
            word_prob = words_prob_dict[word]
            pred_pos_prob += math.log((words_pos_prob_dict[word] * pos_prob) / word_prob)
            pred_neg_prob += math.log((words_neg_prob_dict[word] * neg_prob) / word_prob)
        except:
            pass
        
    if pred_pos_prob > pred_neg_prob:
        return 1
    else:
        return 0

testpredspos = rdd_test_pos.map(predict).collect()
testpredsnegs = rdd_test_neg.map(predict).collect()

print "Test Accuracy Results"
print "----------------------"
print "Positive", sum(testpredspos)/float(len(testpredspos))
print "Negegative", (len(testpredsnegs) - sum(testpredsnegs))/float(len(testpredsnegs))
print "Accuracy", (sum(testpredspos) + (len(testpredsnegs) - sum(testpredsnegs))) / (float(len(testpredsnegs)) + len(testpredspos))












