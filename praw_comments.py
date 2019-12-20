import praw
import csv
import sys
import time
import pandas as pd
import os.path

import atexit

reddit = praw.Reddit(client_id = 'ho02yOl_wIxFeg',
					client_secret = 'et-Bx6IloO6Lw1N2C1Val6GB9Q4',
					username = 'yta_bot',
					password = 'BAthesis2019',
					user_agent = 'yta_botv1')
					
aita = reddit.subreddit('AmITheAsshole')

labels = ['nta', 'nah', 'yta', 'esh']

USAGE = 'This script takes submissions gathered using pushshift.py and pulls their comments. These comments are used to label the submissions. The comments can be saved or discarded. The input parameters are (1) input file containing submissions from pushshift.py (2) OPTIONAL file for saving comments (will be very large)\n\n***NOTE*** this script requires Reddit credentials. For more information, see the PRAW section of the readme\n\nExample call:\n\npython3 praw_comments.py pushshift_results.tsv optional_comment_corpus.tsv'

SAVE_COMMENTS = False

if len(sys.argv) < 2:
	print(USAGE)
	exit(0)
	
input_file = sys.argv[1]	
	
if len(sys.argv) > 2:
	SAVE_COMMENTS = True
	comment_file = sys.argv[2]
	
if not os.path.exists(input_file):
	print('input file not found. please run pushshift.py first and use its result file as the input for this script.')
	exit(0)
	
if SAVE_COMMENTS and not os.path.exists(comment_file):
	f = open(comment_file, 'w')
	f.write('comment_id\tsubmission_id\tscore\tvote\ttext\tauthor\n')
	f.close()
	
	
def extract_comment_vote(text):
	nta = ['NTA', 'YWNBTA', 'Nta', 'Ywnbta', 'nta ', 'ywnbta', 'WNBTA', 'Wnbta']
	nah = ['NAH', 'Nah', 'nah']
	yta = ['YTA', 'YWBTA', 'WBTA', 'Yta', 'Ywbta', 'Wbta', 'yta ', 'ywbta', 'wbta', 'YAH']
	esh = ['ESH', 'Esh']
	shp = ['SHP', 'Shp', 'shp', 'SHITPO', 'Shitpo', 'shitpo']
	info = ['INFO', 'Info']
	classes = [nta, nah, yta, esh, shp, info]
	classes_string = ['nta', 'nah', 'yta', 'esh', 'shp', 'info', 'other']
	
	"""
	class indices
				NTA	...	0
				NAH	...	1
				YTA	...	2
				ESH	...	3
				SHP	...	4
				INFO	...	5
				other	...	6
	"""
	
	class_index = 6	#starts at 6, assuming no class found
	lowest_i = -1 #stores position of first occurence of a keyword
	for class_i in range(len(classes)):
		if lowest_i == 0:
			break
		for keyword in classes[class_i]:
			found_i = text.find(keyword)
			if found_i >= 0 and (found_i < lowest_i or lowest_i < 0):
				lowest_i = found_i
				class_index = class_i
	
	return classes_string[class_index]
	
def calc_label_percentage(votes):
	m = max(votes)
	s = float(sum(votes))
	if s <= 0:
		return 1.0
	res = m/s
	if res > 1.0:
		return 1.0
	return res
		
def calc_pos_percentage(votes):
	p = votes[0] + votes[1]
	s = sum(votes)
	if s <= 0 and p > 0:
		return 1.0
	elif s <= 0 and p < 0:
		return 0.0
	res = p/s
	if res > 1.0:
		return 1.0
	if res < 0.0:
		return 0.0
	return res
	
corpus = pd.read_csv(input_file, sep='\t')

def exit_handler():
    print('\nSaving progress.')
    corpus.to_csv(input_file, sep='\t', index=False)

atexit.register(exit_handler)

if not 'label' in corpus.columns:
	corpus['label'] = 'not yet calculated'
	corpus['label_percentage'] = 'not yet calculated'
	corpus['pos/neg'] = 'not yet calculated'
	corpus['pos_percentage'] = 'not yet calculated'
	corpus['nta'] = 'not yet calculated'
	corpus['nah'] = 'not yet calculated'
	corpus['yta'] = 'not yet calculated'
	corpus['esh'] = 'not yet calculated'
	corpus = corpus[['id', 'label', 'label_percentage', 'pos/neg', 'pos_percentage', 'nta', 'nah', 'yta', 'esh', 'title', 'text', 'score', 'author', 'num_comments']]
	
for ind in corpus.index:
	if ind%100 == 0:
		corpus.to_csv(input_file, sep='\t', index=False)
	
	print(str(ind+1) + ' of ' + str(len(corpus.index)), end="\r")
	
	if 'not yet calculated' not in corpus.iloc[ind].to_list():
		continue
		
	submission_label = [0, 0, 0, 0]
	#pull submission comments using praw
	submission = reddit.submission(id=corpus['id'][ind])
	submission.comments.replace_more(limit=0)
	#save relevant data from comment
	for comment in submission.comments:
		comment_id = str(comment.id)
		submission_id = corpus['id'][ind]
		comment_score = str(comment.score)
		comment_text = str(comment.body.replace('\n', ' ').replace('&amp;#x200B;', ''))
		comment_vote = extract_comment_vote(comment_text)
		comment_author = str(comment.author)
		if comment_author == 'AutoModerator':
			continue
		#adjust submission label according to comment vote and score
		if comment_vote == 'nta':
			submission_label[0] += int(comment_score)
		if comment_vote == 'nah':
			submission_label[1] += int(comment_score)
		if comment_vote == 'yta':
			submission_label[2] += int(comment_score)
		if comment_vote == 'esh':
			submission_label[3] += int(comment_score)
		
		if SAVE_COMMENTS:
			f = open(comment_file, 'a')
			f.write(comment_id + '\t' + submission_id + '\t' + comment_score + '\t' + comment_vote + '\t' + comment_text + '\t' + comment_author + '\n')
			f.close()
	
	max_index = submission_label.index(max(submission_label))
	corpus.at[ind, 'label'] = labels[max_index]
	
	corpus.at[ind, 'label_percentage'] = str(round(calc_label_percentage(submission_label), 2))
	if (submission_label[0] + submission_label[1]) > (submission_label[2] + submission_label[3]):
		corpus.at[ind, 'pos/neg'] = 'pos'
	elif (submission_label[0] + submission_label[1]) < (submission_label[2] + submission_label[3]):
		corpus.at[ind, 'pos/neg'] = 'neg'
	else:
		corpus.at[ind, 'pos/neg'] = 'undecided'
	corpus.at[ind, 'pos_percentage'] = str(round(calc_pos_percentage(submission_label), 2))
	corpus.at[ind, 'nta'] = str(submission_label[0])
	corpus.at[ind, 'nah'] = str(submission_label[1])
	corpus.at[ind, 'yta'] = str(submission_label[2])
	corpus.at[ind, 'esh'] = str(submission_label[3])
	
	
