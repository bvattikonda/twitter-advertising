#!/usr/bin/env python

# Identify the number of tweets that these advertisers send from their
# own profile domain

import sys
import datetime
import string
import optparse
import os
import json
import ast
from urlparse import urlparse
from analysis import *
from users_with_website import user_has_website

def setup_parser():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'What are the\
            properties of redirects employed by these marketers?',
            usage = usage)
    parser.add_option('-s', help = 'Sponsored Tweets users')
    parser.add_option('-a', help = 'Adly users')
    parser.add_option('-w', help = 'Warrior Forums users')
    parser.add_option('--data_dir', help = 'Data directory')
    parser.add_option('--outfile', help = 'File to which output (if\
        any) has to be written')
    return parser

def correct_options(options):
    if not options.data_dir or not os.path.exists(options.data_dir)\
        or not options.outfile:
        return False
    if not options.a or not options.s or not options.w:
        return False
    return True

def share_of_tweets_from_self(user_id, data_dir, profile_domain):
    linksfile = open(os.path.join(data_dir, str(user_id) + '.links'),\
            'r')
    tweets_for_profile_domain = 0
    total_urls = 0
    for line in linksfile:
        destination_domain = get_destination_domain(line)
        if not destination_domain:
            continue
        total_urls += 1
        if destination_domain == profile_domain:
            tweets_for_profile_domain += 1
    if not total_urls:
        return None
    return tweets_for_profile_domain / float(total_urls)


def user_profile_domain(user_id, data_dir):
    userfile = open(os.path.join(data_dir,\
        str(user_id) + '.txt'), 'r')
    try:
        userinfo = json.loads(userfile.readline().strip())
    except ValueError:
        return False
    try:
        if userinfo['url']:
            return get_domain(userinfo['url'])
    except KeyError:
        pass
    return None

def get_self_share(network, user_id, data_dir, outfile):
    profile_domain = user_profile_domain(user_id,\
            data_dir)
    if not profile_domain:
        return
    share = share_of_tweets_from_self(user_id, data_dir,\
            profile_domain)
    if not share: 
        return 
    outfile.write(network + ' ' + str(share) + '\n')

def main():
    parser = setup_parser()
    (options, args) = parser.parse_args()
    if not correct_options(options):
        parser.print_help()
        sys.exit(1)

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)

    outfile = open(options.outfile, 'w')
    for user_id in fetched_adlyusers:
        get_self_share('Adly', user_id, options.data_dir, outfile)
    for user_id in fetched_spntwusers:
        get_self_share('SpnTw', user_id, options.data_dir, outfile)
    for user_id in fetched_warriors:
        get_self_share('Warrior', user_id, options.data_dir, outfile)

if __name__ == '__main__':
    main()
