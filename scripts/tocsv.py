#/usr/bin/env python3

'''
Script to convert comment data to .csv
'''

import pandas as pd
import sys


def load_data(path, dates_D):
    reddit_ids = []
    data = []
    with open(path, 'r', newline='\n') as f:
        for line in f:
            reddit_id, comments = line.split('\t', maxsplit=1)
            if reddit_id in dates_D.keys():
                data.append(comments)
                reddit_ids.append(reddit_id)
    return reddit_ids, data
	
def load_dates(path):
    dates_D = {}
    with open(path, 'r', newline='\n') as f:
        for line in f:
            reddit_id, field = line.strip().split('\t', maxsplit=1)
            dates_D[reddit_id] = field
    return dates_D
	
# read
dates = load_dates(sys.argv[1])
reddit_ids, data_samples = load_data(sys.argv[2], dates)

# output as .csv, easier for R to read in
df = pd.DataFrame(list(zip(reddit_ids, [(dates[reddit_id]) for reddit_id in reddit_ids], data_samples)))
df.to_csv(sys.argv[3])
