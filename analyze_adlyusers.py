#!/usr/bin/env python 

import sys
import os
import optparse
import json
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

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Analyze adly\
                users', usage = usage)
    parser.add_option('--users', help = 'Adly raw data')
    return parser

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

def correct_options(options):
    if not options.users:
        return False
    if not os.path.exists(options.users):
        return False

    return True

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    users = analyze_users(options.users)
    users = sorted(users, key = lambda user: user.followers_count)
    for user in users:
        print '%d\t%s' % (user.user_id, user.screen_name)

if __name__ == '__main__':
    main()
