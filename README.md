# AITA
Corpus of texts from reddit.com/r/amitheasshole

This corpus contains

Submission ID, Label, NTA votes, NAH votes, YTA votes, ESH votes, Title, and Text

of 69959 submissions.

BUILD YOUR OWN CORPUS

use pushshift.py and praw_comments.py to build your own corpus.


(1)

you will need a reddit account to build your corpus. go to http://www.reddit.com to make an account and then follow the instructions on these websites to your credentials.

https://praw.readthedocs.io/en/latest/getting_started/quick_start.html

https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps

enter these credentials into praw_comments.py.

(2)

run pushshift.py. This script uses pushshift.io to scrape submission data and metadata from r/AmITheAsshole. The results are saved in a tsv file. The input parameters are (1) destination file (new results will be appended), (2) starting i, (3) ending i. Submissions are pulled by day of posting based on i, where today is i=0, yesterday i=1, etc. Here is an example call to pull all submissions from the last 80 days:

python3 pushshift.py submissions.tsv 0 80

(3)

run praw_comments.py. This script takes submissions gathered using pushshift.py and pulls their comments. These comments are used to label the submissions. The comments can be saved or discarded. The input parameters are (1) input file containing submissions from pushshift.py (2) OPTIONAL file for saving comments (will be very large)

***NOTE*** 

this script requires Reddit credentials. These credentials must be manually input into the file where you see

reddit = praw.Reddit(client_id = '',
					client_secret = '',
					username = '',
					password = '',
					user_agent = '')

Example call:

python3 praw_comments.py pushshift_results.tsv optional_comment_corpus.tsv
