#!/usr/bin/env python

# Identify the domains to which users are sent to by advertisers.

import sys
import datetime
import string
import optparse
import os
import json
import ast
import urllib
from urlparse import urlparse
from collections import defaultdict
from analysis import *

domains_usagefile = open('domains_usagefile.txt', 'w')
youtubefile = open('youtube_videos.txt', 'w')

def sum_dicts(first, second):
    for key, value in first.iteritems():
        second[key] += value
    return second
     
def get_domain(baseURL, redirects):
    return_domain = urlparse(baseURL).netloc.lower()
    url = baseURL
    try:
        redirect_list = ast.literal_eval(redirects)
    except SyntaxError:
        return
    for i in xrange(1, len(redirect_list) + 1):
        domain = urlparse(redirect_list[-1][1]).netloc.lower()
        if len(domain) > 0:
            return_domain = domain
            url = redirect_list[-1][1]
            break
    if return_domain == 'bitly.com' and 'warning' in url:
        url = urllib.unquote(url.split('=', 1)[1])
        return_domain = urlparse(url).netloc.lower()
    if return_domain == 'www.youtube.com' or return_domain ==\
        'youtube.com':
        print urllib.unquote(url)
        youtubefile.write(urllib.unquote(url) + '\n')
    return return_domain

def get_domain_usage(data_dir, user_id):
    domain_tweets = defaultdict(int)
    linksfilename = os.path.join(data_dir, str(user_id) + '.links')
    linksfile = open(linksfilename, 'r')
    for line in linksfile:
        try:
            date, baseURL, success_str, redirects = line.strip().split('\t')
            success = json.loads(success_str)
        except ValueError:
            continue
        if success:
            domain = get_domain(baseURL, redirects)
            if domain:
                domain_tweets[domain] += 1
    return domain_tweets

def user_domains(category, data_dir, users): 
    global_domains_usage = defaultdict(int)
    for user_id in users:
        domains_usage = get_domain_usage(data_dir, user_id)
        sum_dicts(domains_usage, global_domains_usage)

    for key, value in global_domains_usage.iteritems():
        if isinstance(key, unicode):
            print 'Unicode:', key
            key = key.encode('utf8', 'ignore')
        domains_usagefile.write(category + '\t' + str(key) + '\t' +\
                str(value) + '\n')

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)

    user_domains('Adly', options.data_dir, fetched_adlyusers) 
    user_domains('SpnTw', options.data_dir, fetched_spntwusers) 
    user_domains('Warrior', options.data_dir, fetched_warriors) 

    domains_usagefile.close()

if __name__ == '__main__':
    main() 
