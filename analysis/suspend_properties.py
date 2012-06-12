#!/usr/bin/env python

# Identify properties of the accounts that have been suspended

import sys
import string
import optparse
import os
import json
from datetime import datetime
import ast
from urlparse import urlparse
from collections import namedtuple
from HTMLParser import HTMLParser
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    '..'))
import logging

AccountProperties = namedtuple('AccountProperties', ['life',\
        'suspension'])
begin_2011 = datetime(2011, 1, 1)
        
def setup_parser():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Properties of the\
            accounts that have been suspended', usage = usage)
    parser.add_option('-s', '--suspended_users', help = 'File which\
            has the user ids of all the users who have been suspended')
    parser.add_option('--data_dir', help = 'Data directory')
    parser.add_option('--outfile', help = 'File to which output (if\
        any) has to be written')
    return parser

def correct_options(options):
    if not options.data_dir or not os.path.exists(options.data_dir)\
        or not options.outfile:
        return False
    return True

def account_properties(data_dir, user_id):
    try:
        userfile = open(os.path.join(data_dir, str(user_id) + '.txt'))
    except IOError:
        return None
    try:
        userinfo = json.loads(userfile.readline().strip())
        userfile.readline()
        userfile.readline()
    except:
        return None
    
    while True:
        line = userfile.readline()
        if line == '':
            break
        last_line = line
    try:
        last_tweet = json.loads(last_line)
    except:
        return None
    account_start = datetime.strptime(userinfo['created_at'], '%a %b\
                            %d %H:%M:%S +0000 %Y')
    account_end = datetime.strptime(last_tweet['created_at'], '%a %b\
                            %d %H:%M:%S +0000 %Y')
    return AccountProperties(account_end - account_start, account_end) 

def main():
    parser = setup_parser()
    (options, args) = parser.parse_args()
    if not correct_options(options):
        parser.print_help()
        sys.exit(1)
    sfile = open(options.suspended_users)
    suspended_users = list()
    for line in sfile:
        (network, user_id) = line.strip().split(' ')
        suspended_users.append((network, user_id))

    outfile = open(options.outfile, 'w')
    for network, user_id in suspended_users:
        props = account_properties(options.data_dir, user_id)
        if props:
            outfile.write(str(props.life.days) + '\t' +\
                    str((props.suspension - begin_2011).days) + '\n')

if __name__ == '__main__':
    main()
