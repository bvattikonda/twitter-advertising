#!/usr/bin/env python 

# Test script to quickly run some REST API calls and find out how the response
# is being parsed

import sys
import os
import ast
import cPickle
import argparse
from datetime import datetime
from collections import defaultdict
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from api_functions import *
from constants import *

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def convert_to_user_ids(api_info, screennames):
    total = len(screennames)
    count = 0
    final_user_list = list()
    while True:
        if count >= total:
            break
        user_info_list, success = block_on_call(api_info,\
            'lookup_users',\
            screen_names = screennames[count:count+min(100,total - count)])
        final_user_list.extend(user_info_list)
        count = count + 100
    return final_user_list

def get_args():
    parser = argparse.ArgumentParser(description = 'Get user details')
    parser.add_argument('--authfile', required = True,\
        help = 'File with all the authentication details of applications')
    parser.add_argument('--screennames', required = True,\
        help = 'File with screen names of users whose ids have to be fetched')
    parser.add_argument('--outfile', required = True,\
        help = 'File to which output has to be written')
    return parser.parse_args()

def main():
    args = get_args()
    api_info = create_api_objects(args.authfile)
    print_remaining_hits(api_info)
    screennamesfile = open(args.screennames, 'r')
    screennames = list()
    for line in screennamesfile:
        screennames.append(line.strip())
    final_user_list = convert_to_user_ids(api_info, screennames)
    file = open(args.outfile, 'w')
    for user in final_user_list:
        file.write(str(user['id']) + ' ' +\
            user['screen_name'] + '\n')

if __name__ == '__main__':
    main()
