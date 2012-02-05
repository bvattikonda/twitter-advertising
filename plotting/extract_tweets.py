#!/usr/bin/env python 

import sys
import os
import simplejson as json
import time
import ast
import argparse
from datetime import datetime

def get_args():
    parser = argparse.ArgumentParser(description = 'Extract just tweets')
    parser.add_argument('--user_info', required = True,\
        help = 'Text file which has the user info')
    parser.add_argument('--outfile', required = True,\
        help = 'File to which tweets have to be written')
    return parser.parse_args()

def extract_list(line):
    return ast.literal_eval(line)

def extract_tweets(user_infofilename, outfilename):
    outfile = open(outfilename, 'w')
    user_infofile = open(user_infofilename, 'r')
    user_infofile.readline()
    user_infofile.readline()
    user_infofile.readline()
    tweets = extract_list(user_infofile.readline().strip())
    for tweet in tweets:
        for url in tweet['entities']['urls']:
            if url['expanded_url'] and 'twitpic' not in url['expanded_url']:
                print tweet['text'], url['expanded_url']

def main():
    args = get_args()
    extract_tweets(args.user_info, args.outfile)

if __name__ == '__main__':
    main()
