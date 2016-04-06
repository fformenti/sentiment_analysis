__author__ = 'felipeformentiferreira'

import sys
import json

#---- creating a dictionary --------

afinnfile = open("AFINN-111.txt")
scores = {} # initialize an empty dictionary
for line in afinnfile:
  term, score  = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
  scores[term] = int(score)  # Convert the score to an integer.

#---- parsing txt file into json object ------

my_output = []
with open('problem_1_submission.txt') as f:
    for line in f:
        my_output.append(json.loads(line))

#---- separating the text message from other fields

text_list = []
for tweet in my_output:
    if 'text' in tweet:
        text_list.append(tweet['text'])


#print text_list

#---- spliting the words inside the tweet and summing

score_list = []
total_score = 0
for text in text_list:
    words = text.split(" ")
    for word in words:
        if word in scores:
            value = scores[word]
        else:
            value = 0
        total_score = total_score + value
        score_list.append(total_score)
    print total_score
    total_score = 0

print score_list
