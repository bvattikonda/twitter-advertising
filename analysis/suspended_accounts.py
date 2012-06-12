#!/usr/bin/env python

# Identify the tools that advertisers use to send the Tweets

import sys
import datetime
import string
import optparse
import os
import json
import ast
from urlparse import urlparse
from collections import defaultdict
from HTMLParser import HTMLParser
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    '..'))
import logging
from api_functions import *

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'How many users of\
                each kind', usage = usage)
    parser.add_option('-s', help = 'Sponsored Tweets users')
    parser.add_option('-a', help = 'Adly users')
    parser.add_option('-w', help = 'Warrior Forums users')
    parser.add_option('--data_dir', help = 'Data directory')
    parser.add_option('--authfile', action = 'store',\
        help = 'Authentication details file')
    parser.add_option('--outfile', help = 'File to which output (if\
        any) has to be written')
    return parser

def load_users(usersfilename):
    usersfile = open(usersfilename, 'r')
    user_ids = set()
    for line in usersfile:
        splitline = line.strip().split('\t')
        user_id = int(splitline[0])
        user_ids.add(user_id)
    return user_ids

def fetched(user_ids, extension, data_dir):
    fetched_userids = set()
    for user_id in user_ids:
        if os.path.exists(os.path.join(data_dir, str(user_id) +\
            extension)):
            fetched_userids.add(user_id)
    return fetched_userids

def get_active_users(api_info, _users):
    users = list(_users)
    total = len(users)
    count = 0
    active_users = set()
    while True:
        if count >= total:
            break
        user_info_list, success = block_on_call(api_info,\
                'lookup_users',\
                user_ids = users[count:count + min(100, total -\
                count)])
        for user_info in user_info_list:
            active_users.add(user_info['id'])
        print 'Resolved %d out of %d' % (count, total)
        count += 100
    return active_users
    
def correct_options(options):
    if not options.a or not options.s or not options.w:
        return False
    if not options.data_dir or not options.authfile or not\
        options.outfile:
        return False
    if not os.path.exists(options.data_dir) or not\
        os.path.exists(options.authfile):
        return False
    return True
 
def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    api_info = create_api_objects(options.authfile)

    logging.basicConfig(filename = os.path.join(options.data_dir,\
        'suspended_users.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)
    
    active_adlyusers = get_active_users(api_info, fetched_adlyusers)
    outfile = open(options.outfile, "w")
    for user in active_adlyusers:
        outfile.write('Adly ' + str(user) + "\n")

    active_spntwusers = get_active_users(api_info, fetched_spntwusers)
    for user in active_spntwusers:
        outfile.write('SpnTW ' + str(user) + '\n')

    active_warriors = get_active_users(api_info, fetched_warriors)
    for user in active_warriors:
        outfile.write('Warrior ' + str(user) + '\n')

if __name__ == '__main__':
    main() 
