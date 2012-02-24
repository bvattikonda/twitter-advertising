#!/usr/bin/env python 

# Find out how much of the user history do we have 

import sys
import os
import json
import time
import ast
import optparse
from datetime import datetime
from analysis import *

def main():
    parser = parse_args()
    options = parser.parse_args()[0]

    print '--- User history we have'
    userfilenames = os.listdir(options.data_dir)
    total_count = 0
    complete_count = 0
    partial = list()
    for userfilename in userfilenames:
        if not userfilename.endswith('.txt'):
            continue
        user_id = int(userfilename.replace('.txt',''))
        userfile = open(os.path.join(options.data_dir, userfilename),
                    'r')
        try:
            userinfo = json.loads(userfile.readline().strip())
        except:
            continue
        statuses_count = userinfo['statuses_count']
        if userinfo['statuses_count'] < 3200:
            complete_count += 1 
            total_count += 1
            continue
        try:
            userfile.readline()
            userfile.readline()
        except:
            continue
        try:
            tweet_count = 0
            line = userfile.readline()
            tweet = json.loads(line.strip())
            start_time = time.strptime(tweet['created_at'], '%a %b\
                        %d %H:%M:%S +0000 %Y')
            last_line = line
            while len(line) > 0:
                tweet_count += 1
                last_line = line
                line = userfile.readline()
            tweet = json.loads(last_line.strip())
            end_time = time.strptime(tweet['created_at'], '%a %b\
                        %d %H:%M:%S +0000 %Y')
            total_count += 1
        except ValueError:
            print user_id,line, len(line), userfile.name
            raise
            print complete_count, total_count, end_time, start_time
        tweet_share = tweet_count / float(userinfo['statuses_count'])
        account_time = time.strptime(userinfo['created_at'], '%a %b\
                        %d %H:%M:%S +0000 %Y')
        account_lifetime = (time.time() - time.mktime(account_time))
        tweet_window = time.mktime(end_time) - time.mktime(start_time)
        time_share = tweet_window / account_lifetime
        partial.append((tweet_share, time_share))
    print complete_count, total_count
    f = open('temp.txt', 'w')
    for (tw, ti) in partial:
        f.write(str(tw) + '\t' + str(ti) + '\n')

if __name__ == '__main__':
    main()
