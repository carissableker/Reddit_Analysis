#!/usr/bin/env python3

'''
Script to grab the submission data for a given time frame within a given subreddit
'''

import os
import re
import sys

import praw

from calendar import monthrange
import time
import datetime

def get_flat_comments(submission):
    flat_comment = ''
    submission.comments.replace_more(limit=0)
    for comment in submission.comments.list():
        if not comment.body == '[deleted]' or comment.body == '[removed]':
            flat_comment += comment.body + ' '
    return flat_comment
    
def clean_flat_comments(document):
    document = document.encode(encoding='ascii', errors='ignore').decode('ascii')
    document = document.replace('\n', ' ')
    document = document.replace('\t', ' ')
    return document 

def main():
    os.chdir('../data')
    outfile = '{subreddit}_{startYear}_{startMonth}-{stopYear}_{stopMonth}_flatcomments.txt'.format(**{'subreddit':args.subreddit, \
            'startYear':args.startYear, 'startMonth':args.startMonth, 'stopYear':args.stopYear,  'stopMonth':args.stopMonth})

    if os.path.exists(outfile):
        print('%s already exits. Are you sure you want to rerun? \nPlease delete the file and try again. '%outfile)
        sys.exit()

    reddit = praw.Reddit(client_id='xxxxxxx',
                         client_secret='xxxxx',
                         user_agent='xxxxxxxxxx',
                         username='xxxxxx',
                         password='xxxxx')
                     
    sub = reddit.subreddit(args.subreddit)

    timestamp_Start = time.mktime(datetime.datetime(args.startYear, args.startMonth, 1, 0, 0, 0).timetuple())
    timestamp_Stop = time.mktime(datetime.datetime(args.stopYear, args.stopMonth, monthrange(args.stopYear, args.stopMonth)[1], 23, 59, 59, 99).timetuple())
    print('Start:', timestamp_Start)
    print('Stop:', timestamp_Stop)

    submissions = []
    for submission in sub.submissions(start=timestamp_Start, end=timestamp_Stop):
        if submission.num_comments > args.num_comments:
                submissions.append(submission)
    
    gc = get_flat_comments
    cc = clean_flat_comments
    with open(outfile, 'w') as f:
        for i, submission in enumerate(submissions):
            document = gc(submission=submission)
            document = cc(document)
            f.write(submission.id + '\t' + document + '\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit",help="Name of the Subreddit")
    parser.add_argument("startYear",help="Start timestamp year",type=int)
    parser.add_argument("startMonth",help="Start timestamp month",type=int)
    parser.add_argument("stopYear",help="Stop timestamp year",type=int)
    parser.add_argument("stopMonth",help="Stop timestamp month",type=int)
    parser.add_argument("-n", "--num_comments", help="Minimum number of comments", type=int, default=100)
    args = parser.parse_args()
    main()

