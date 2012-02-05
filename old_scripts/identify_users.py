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

adwords = ['advertisement', 'sponsored', 'ad']
old_ad_texts = cPickle.load(open('scratch/texts.pickle', 'rb'))
ad_texts = {}

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_ad_patterns():
    ad_patterns = []
    for adword in adwords:
        ad_patterns.append(re.compile('^' + adword + '[: ]| ' +\
        adword + '[: ]', flags = re.I))
    return ad_patterns

def isAd(ad_patterns, status):
    for hashtag in status.entities['hashtags']:
        if hashtag['text'] == 'ad':
            return True
    for ad_pattern in ad_patterns:
        if re.search(ad_pattern, status.text):
            return True

def get_ad_domains(ad_patterns, statuses):
    ad_domains = set()
    for status in statuses:
        if isAd(ad_patterns, status):
            for url in status.entities['urls']:
                if url['expanded_url']:
                    ad_domain = urlparse.urlparse(url['expanded_url']).netloc
                    ad_texts[ad_domain] = (status.text, url['expanded_url'])
                    ad_domains.add(ad_domain)
    return ad_domains

def main():
    status_pickle_dir = sys.argv[1]
    count = 0 
    old_ad_domains = cPickle.load(open('scratch/domains.pickle', 'rb'))
    ad_domains = set()
    ad_patterns = get_ad_patterns()
    while True:
        pickle_file = os.path.join(status_pickle_dir,\
            'sample_' + str(count) + '_' + str(count + 1000))
        if not os.path.exists(pickle_file):
            break
        if count == 80000:
            break
        print count
        statuses = cPickle.load(open(pickle_file, 'rb'))
        ad_domains = ad_domains | get_ad_domains(ad_patterns, statuses)
        count = count + 1000
    print len(ad_domains)
    for ad_domain in old_ad_domains:
        ad_domains.discard(ad_domain)
    for key in old_ad_texts:
        if key in ad_texts:
            del ad_texts[key]
    print len(ad_domains)
    # print ad_domains
    # for k, v in ad_texts.items():
    #     print k, v
    cPickle.dump(ad_domains, open('domains1.pickle', 'wb'), 2)
    cPickle.dump(ad_texts, open('texts1.pickle', 'wb'), 2)
if __name__ == '__main__':
    main()
