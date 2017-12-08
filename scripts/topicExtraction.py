#!/usr/bin/env python3

'''
Use NMF to extract topics from Reddit comments.
Can be run commandline or imported as a module.
'''

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

import time
import datetime

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF

from collections import defaultdict

class redditNMF(object):

    def __init__(self, subreddit, startYear, startMonth, stopYear, stopMonth, n_features=1000, n_components=10):
        self.subreddit = subreddit 
        self.startYear = startYear 
        self.startMonth = startMonth
        self.stopYear = stopYear
        self.stopMonth = stopMonth
        
        self.n_features = n_features
        self.n_components = n_components
        
        submission_dates_file = '../data/{subreddit}_{startYear}_{startMonth}-{stopYear}_{stopMonth}_submissiondates.txt'.format(\
                **{'subreddit':subreddit, 'startYear':startYear, 'startMonth':startMonth, 'stopYear':stopYear,  'stopMonth':stopMonth})
        flat_comments_file = '../data/{subreddit}_{startYear}_{startMonth}-{stopYear}_{stopMonth}_flatcomments.txt'.format(\
                **{'subreddit':subreddit, 'startYear':startYear, 'startMonth':startMonth, 'stopYear':stopYear,  'stopMonth':stopMonth})
        
        # load data 
        self.dates = self._load_dates(submission_dates_file)
        self.reddit_ids, self.data_samples = self._load_data(flat_comments_file, self.dates)
        self.n_samples = len(self.data_samples)
    
        # parse data
        self.tfidf, self.feature_names = self.tf_idf()

        # model
        self.nmf = self.nmf()
    
        # topics
        self.W, self.W_per_date = self.order()
        
        
    def _load_dates(self, path):
        dates_D = {}
        with open(path, 'r', newline='\n') as f:
            for line in f:
                reddit_id, field = line.strip().split('\t', maxsplit=1)
                dates_D[reddit_id] = field
        return dates_D

    def _load_data(self, path, dates_D):
        reddit_ids = []
        data = []
        with open(path, 'r', newline='\n') as f:
            for line in f:
                reddit_id, comments = line.split('\t', maxsplit=1)
                if reddit_id in dates_D.keys():
                    data.append(comments)
                    reddit_ids.append(reddit_id)
        return reddit_ids, data
    
    def tf_idf(self):
        # Use tf-idf features for NMF.
        print("Extracting tf-idf features for NMF...", end=' ')
        tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2,
                                           max_features=self.n_features,
                                           stop_words='english')
        t0 = time.time()
        tfidf = tfidf_vectorizer.fit_transform(self.data_samples)
        print("done in %0.3fs." % (time.time() - t0))

        feature_names = tfidf_vectorizer.get_feature_names()
        return tfidf, feature_names
    
    def nmf(self):
        # Fit the NMF model
        print("Fitting the NMF model (Frobenius norm) with tf-idf features, "
              "n_samples=%d and n_features=%d..."
              % (self.n_samples, self.n_features), end=' ')
        t0 = time.time()
        nmf = NMF(n_components=self.n_components, random_state=1,
                  alpha=.1, l1_ratio=.5).fit(self.tfidf)
        print("done in %0.3fs." % (time.time() - t0))
        return nmf

    def top_words(self, n_top_words):
        messages = defaultdict(list)
        for topic_idx, topic in enumerate(self.nmf.components_):
            messages[topic_idx] =  [self.feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]
        return dict(messages)
            
    def order(self):
        index = pd.MultiIndex.from_tuples(tuples=[(reddit_id, self.dates[reddit_id]) for reddit_id in self.reddit_ids], names=['submission_id', 'Date'])
        W = pd.DataFrame(self.nmf.fit_transform(self.tfidf), index=index)
        W.sort_index(inplace=True)
        W_per_date = (W>0).groupby('Date').sum()
        return W, W_per_date

    def heatmap(self, per_day=True):
        if per_day:
            sns.heatmap(self.W_per_date)
        else:
            sns.heatmap(self.W)
        plt.yticks(rotation=0) 
        plt.xlabel('Topic')

    
    def timeseries(self, topic='all'):
        if topic == 'all':
            self.W_per_date.plot(rot=20)
        elif topic in range(self.nmf.components_.shape[0]):
            self.W_per_date[topic].plot(rot=20)
        else:
            print('Topic %s out of range'%str(topic))

    def save_results(self, n_top_words=20):
        topics_file = '../data/{subreddit}_{startYear}_{startMonth}-{stopYear}_{stopMonth}_topics.txt'.format(\
                **{'subreddit':self.subreddit, 'startYear':self.startYear, 'startMonth':self.startMonth, \
                'stopYear':self.stopYear,  'stopMonth':self.stopMonth})

        with open(topics_file, 'w') as out:
            out.write('#%i\t%i\n'%(self.n_components, self.n_features))
            # write topics
            for topic_idx, topic in enumerate(self.nmf.components_):
                words = ' '.join([self.feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]])            
                out.write('#%i\t%s\n'%(topic_idx, words))

        # write edges
        longiW = self.W.stack()
        longW = longW[longW > 0]
        longW.index.names = ['submission_id', 'Date', 'topic_num']
        longW.to_csv(path=topics_file, sep='\t', header=True, mode='a')
        
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("subreddit",help="Name of the Subreddit")
    parser.add_argument("startYear",help="Start timestamp year",type=int)
    parser.add_argument("startMonth",help="Start timestamp month",type=int)
    parser.add_argument("stopYear",help="Stop timestamp year",type=int)
    parser.add_argument("stopMonth",help="Stop timestamp month",type=int)
    args = parser.parse_args()
    model = redditNMF(args.subreddit, args.startYear, args.startMonth, args.stopYear, args.stopMonth)
    model.save_results()


