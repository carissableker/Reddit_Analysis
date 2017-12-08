#!/usr/bin/env python3

'''This script grabs the authors associated with a list of submission files. Input 
is a tab deliminated text file where the first column is a list of Reddit Submission IDs. 
The output files are a list of submission authors and a list of comment authors for each 
submission, but only for commenters who had also added a submission.
'''

import numpy as np
import praw

def main():

    input_file = args.SubmissionFile
    ids = np.loadtxt(input_file,delimiter='\t',usecols=(0,),dtype=str)

    reddit = praw.Reddit(client_id='xxxxx',
                         client_secret='xxxxxx',
                         user_agent='xxxxxxx',
                         username='xxxxxx',
                         password='xxxxxxx')

    outfile = input_file.rsplit('_',maxsplit=1)[0] + '_submissionAuthors.txt'
    outfile2 = input_file.rsplit('_',maxsplit=1)[0] + '_commentAuthors.txt'

    authors = []

    with open(outfile,"w") as f:
        for i_d in ids:
            submission = reddit.submission(id=i_d)
            if submission.author != None:
                f.write(str(submission.id) + '\t' + "submission" + '\t' + str(submission.author.name) + '\n')
                authors.append(str(submission.author.name))

    with open(outfile2,"w") as f:
        for i_d in ids:
            submission = reddit.submission(id=i_d)
            submission.comments.replace_more(limit=0)
            for comment in submission.comments.list():
                if comment.author != None:
                    if comment.author.name in authors:
                        f.write(str(submission.id) + '\t' + "comment" + '\t' + str(comment.author.name) + '\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("SubmissionFile", help="Name of file, IDs in first column")
    args = parser.parse_args()
    main() 
