#!/usr/bin/env python

import os 
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    '../tweepy'))
from tweepy import *
from datetime import datetime
import cPickle
import inspect
import re
import urlparse
from collections import defaultdict
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    '..'))
from constants import *
from utils import *
import unicodedata

adwords = ['advertisement', 'sponsored', 'ad']

def print_members(element):
    for name, value in inspect.getmembers(element):
        if name == 'tweets' or name.startswith('__'):
            continue
        print name, value

#####################################################################
# Non disclosure by each user
#####################################################################
# return the regular expressions which identify the ads
# return True if the tweet is tagged an Ad
def isMarkedAd(status):
    for hashtag in status.entities['hashtags']:
        if hashtag['text'] == 'ad':
            return True
    for adword_pattern in adword_patterns:
        if re.search(adword_pattern, status.text):
            return True

def isAdTweet(tweet, ad_domain_patterns):
    for url in tweet.entities['urls']:
        if url['expanded_url']:
            for ad_domain_pattern in ad_domain_patterns:
                if re.match(ad_domain_pattern,\
                    urlparse.urlparse(url['expanded_url']).netloc):
                    return True
    return False
         
def getNonDisclosure(user_info, ad_domain_patterns):
    total_ad_tweets = 0
    total_non_disc_tweets = 0
    for tweet in user_info.tweets:
        if not isAdTweet(tweet, ad_domain_patterns):
            continue
        total_ad_tweets = total_ad_tweets + 1
        if not isMarkedAd(tweet):
            total_non_disc_tweets = total_non_disc_tweets + 1
    return total_non_disc_tweets * 100 / float(total_ad_tweets)

# @advertisers_dir: directory which has the pickle files for advertisers
# return list with each users % of non disclosure
def non_disclosure(advertisers_dir):
    non_disclosure_values = list()
    pickle_files = os.listdir(advertisers_dir)
    for pickle_file in pickle_files:
        user_info = cPickle.load(open(os.path.join(advertisers_dir, pickle_file), 'rb'))
        try:
            non_disclosure_values.append(getNonDisclosure(user_info,\
                ad_domain_patterns))
        except ZeroDivisionError:
            pass
    return non_disclosure_values

#####################################################################
# Link statistics
#####################################################################
def updateLinkStats(link_stats, user_info):
    user_link_stats = defaultdict(int)
    for tweet in user_info.tweets:
        for url in tweet.entities['urls']:
            if url['expanded_url']:
                for ad_domain_pattern in ad_domain_patterns:
                    if re.match(ad_domain_pattern,\
                        urlparse.urlparse(url['expanded_url']).netloc):
                        user_link_stats[url['expanded_url']] = 1
    return sum_int_dicts(link_stats, user_link_stats)
    
def repeated_links(advertisers_dir):
    pickle_files = os.listdir(advertisers_dir)
    link_stats = defaultdict(int)
    for pickle_file in pickle_files:
        user_info = cPickle.load(open(os.path.join(advertisers_dir,\
            pickle_file), 'rb'))
        updateLinkStats(link_stats, user_info)
    return link_stats

#####################################################################
# Advertisers, normal users relationships comparison
#####################################################################
def number_of_connections_for_set(pickle_dir):
    pickle_files = os.listdir(pickle_dir)
    connections = list()
    for pickle_file in pickle_files:
        user_info = cPickle.load(open(os.path.join(pickle_dir,\
            pickle_file), 'rb'))
        connections.append((user_info.followers_count,\
            user_info.friends_count))
    return connections
     
def number_of_connections(advertisers_dir, normalusers_dir):
    return number_of_connections_for_set(advertisers_dir),\
        number_of_connections_for_set(normalusers_dir)
        
#####################################################################
# Advertisers, normal users retweet pattern
#####################################################################
def percentage_retweets_for_set(pickle_dir):
    pickle_files = os.listdir(pickle_dir)
    retweets_share = list()
    for pickle_file in pickle_files:
        user_info = cPickle.load(open(os.path.join(pickle_dir,\
            pickle_file), 'rb'))
        retweets = 0
        for tweet in user_info.tweets:
            if tweet.retweeted:
                retweets += 1
        try:
            retweets_share.append(retweets / float(len(user_info.tweets)))
        except ZeroDivisionError:
            pass
    return retweets_share

def percentage_retweets(advertisers_dir, normalusers_dir):
    return percentage_retweets_for_set(advertisers_dir),\
        percentage_retweets_for_set(normalusers_dir)

#####################################################################
# Statistics for different kinds of domains
#####################################################################
def domain_stats(pickle_dir):
    disclosed_ads = defaultdict(int)
    undisclosed_ads = defaultdict(int)
    pickle_files = os.listdir(pickle_dir)
    for pickle_file in pickle_files:
        user_info = cPickle.load(open(os.path.join(pickle_dir,\
            pickle_file), 'rb'))
        for tweet in user_info.tweets:
            for url in tweet.entities['urls']:
                if url['expanded_url']:
                    for ad_domain_pattern in ad_domain_patterns:
                        if re.match(ad_domain_pattern,\
                            urlparse.urlparse(url['expanded_url']).netloc):
                            if isMarkedAd(tweet):
                                disclosed_ads[ad_domain_pattern.pattern] += 1
                            else:
                                undisclosed_ads[ad_domain_pattern.pattern] += 1
    return disclosed_ads, undisclosed_ads

if __name__ == '__main__':
    f = open('temp.txt', 'w')
    print >>f, domain_stats('../data/advertisers_data')
    # print percentage_retweets('../data/advertisers_data',\
    #                              '../data/normalusers_data')
    # print >>f, number_of_connections('../data/advertisers_data',\
    #                                  '../data/normalusers_data')
    # print >> f, repeated_links('../data/advertisers_data')
    # non_disclosure('../data/advertisers_data/')
