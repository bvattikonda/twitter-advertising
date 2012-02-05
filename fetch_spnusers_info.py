#!/usr/bin/env python 

# The goal of this script is to find the information of all the sponsored tweets
# users that we have in our list

import sys
import os
import time
import argparse
import simplejson as json
sys.path.append('spnpy')
from spnpy import *

def get_args():
    parser = argparse.ArgumentParser(description = 'Get user connectivity')
    parser.add_argument('--users', required = True,\
        help = 'File which has the screen names of users')
    parser.add_argument('--outfile', required = True,\
        help = 'File to which the user information should be written')
    return parser.parse_args()

def get_users(usersfilename):
    usersfile = open(usersfilename, 'r')
    users = list()
    for line in usersfile:
        users.append(line.strip())
    return users

def main():
    args = get_args()
    api = API(key = '06cba2c2dc0df8039f8ea0234e1b4fe4')
    outfile = open(args.outfile, 'w')
    users = get_users(args.users)
    total_users = len(users)
    count = 0
    while True:
        if count >= total_users:
            break
        while True:
            user_info = api.lookup_names(screen_names = users[count:count +\
                min(50, total_users - count)])
            if 'error' in user_info:
                time.sleep(1)
                continue
            count = count + min(50, total_users - count)
            for key, value in user_info.iteritems():
                outfile.write(json.dumps(value) + '\n')

if __name__ == '__main__':
    main()
