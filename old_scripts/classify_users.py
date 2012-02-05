#!/usr/bin/env python 

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
import cPickle
import inspect
import urlparse
import re
import unicodedata
from constants import *

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def classify_users(statuses, total_normal_users):
    advertisers = set()
    normal_users = set()
    for status in statuses:
        advertiser = False
        for url in status.entities['urls']:
            if url['expanded_url']:
                for ad_domain_pattern in ad_domain_patterns:
                    if re.match(ad_domain_pattern,\
                        urlparse.urlparse(url['expanded_url']).netloc):
                        advertisers.add(status.user.id)
                        advertiser = True
                        break
            if advertiser:
                break
        if not advertiser:
            if total_normal_users < 20000:
                normal_users.add(status.user.id)
    return advertisers, normal_users

def main():
    status_pickle_dir = sys.argv[1]
    advertisers = set()
    normal_users = set()
    count = 0
    while True:
        pickle_file = os.path.join(status_pickle_dir,\
            'sample_' + str(count) + '_' + str(count + 1000))
        if not os.path.exists(pickle_file):
            break
        print count, len(advertisers), len(normal_users)
        statuses = cPickle.load(open(pickle_file, 'rb'))
        current_advertisers, current_normal_users = classify_users(\
            statuses, len(normal_users))
        advertisers = advertisers | current_advertisers
        normal_users = normal_users | current_normal_users
        count = count + 1000
    print len(advertisers)
    print len(normal_users)
    cPickle.dump(advertisers, open('advertisers1.pickle', 'wb'))
    cPickle.dump(normal_users, open('normal_users1.pickle', 'wb'))

if __name__ == '__main__':
    main()
