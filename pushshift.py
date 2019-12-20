import requests
import sys
import os.path
import re

USAGE = 'This script uses pushshift.io to scrape submission data and metadata from r/AmITheAsshole. The results are saved in a tsv file. The input parameters are (1) destination file (new results will be appended), (2) starting i, (3) ending i. Submissions are pulled by day of posting based on i, where today is i=0, yesterday i=1, etc. Here is an example call to pull all submissions from the last 80 days:\npython3 pushshift.py submissions.tsv 0 80'

header = 'id\tnum_comments\ttitle\ttext\tauthor\tscore\n'

if len(sys.argv) != 4:
	print(USAGE)
	exit(0)

dest_file = sys.argv[1]
start_i = int(sys.argv[2])
end_i = int(sys.argv[3])

def safe_extract(sub, key):
	if key in sub:
		return str(sub[key])
	else:
		return '[deleted]'

def submission_to_str(sub):
	txt = (safe_extract(sub, 'id') + 
	'\t' + safe_extract(sub, 'num_comments') +
	'\t' + safe_extract(sub, 'title') +
	'\t' + re.sub(' +', ' ', safe_extract(sub, 'selftext').replace('\n', ' ').replace('&amp;#x200B;', '').replace('\r', ' ').replace('\t', ' ')) + 
	'\t' + safe_extract(sub, 'author') +
	'\t' + safe_extract(sub, 'score') + '\n')
	return txt
	
if not os.path.exists(dest_file):
	f = open(dest_file, 'w')
	f.write(header)
	f.close()

f = open(dest_file, 'r')

if f.readline() != header:
	print('found different header on file than expected. if using this script to extend previously finished corpus, please create a different destination file, run praw_comments on that, and then append the new finished corpus onto the previous one. example:\n\npython3 pushshift.py newfile.tsv 0 70\n\npython3 praw_comments.py newfile.tsv\n\ntail -n +2 newfile.tsv >> prevcorpus.tsv\n\nthe last line appends the new corpus to the old one (minus the header line)')
	exit(0)

f = open(dest_file, 'a')

total = 0

for i in range(start_i, end_i):
	response = requests.get('https://api.pushshift.io/reddit/search/submission/?subreddit=amitheasshole&after=' + str(i+1) + 'd&before=' + str(i) + 'd&num_comments=>20&size=500')
	json = response.json()
	total = total + len(json['data'])
	print('day: ' + str(i) + '\t' + str(len(json['data'])) + '\ttotal: ' + str(total))
	for submission in json['data']:
		f.write(submission_to_str(submission))
		
f.close()
