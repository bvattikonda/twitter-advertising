#!/usr/bin/env python 

import sys
import os
import argparse
import simplejson as json
from collections import namedtuple
import locale

''' Keys in the dictionary of each user on adly
['client_id', 'extra', 'is_premium', 'twitter_avg_tweets', 'about_publisher',
'id', 'display_name', 'service', 'client_name', 'do_not_sell',
'client_screen_name', 'publisher_id', 'next_available', 'profile_url',
'fee_computation_method', 'profile_image_url', 'gross_margin',
'price_per_tweet', 'proposed_earns', 'name', 'country',
'client_followers_count', 'proposed_price', 'publisher_earns', 'on_adly']
'''

def get_args():
    parser = argparse.ArgumentParser(description = 'Analyze adly users')
    parser.add_argument('--users', required = True,\
        help = 'Text file with all the adly users information')
    return parser.parse_args()

def analyze_users(usersfilename):
    usersfile = open(usersfilename, 'r')
    printed = False
    users = list()
    User = namedtuple('User', ['user_id', 'screen_name', 'followers_count'])
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    for line in usersfile:
        x = json.loads(line.strip())
        if not printed:
            printed = True
            print x['publishers'][0].keys()
        for client_info in x['publishers']:
            users.append(User(client_info['client_id'],\
                client_info['client_screen_name'],\
                locale.atoi(client_info['client_followers_count'])))
    return users

def main():
    args = get_args()
    users = analyze_users(args.users)
    users = sorted(users, key = lambda user: user.followers_count)
    for user in users:
        print user.user_id, user.screen_name

if __name__ == '__main__':
    main()
