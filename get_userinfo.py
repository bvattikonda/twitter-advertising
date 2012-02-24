#!/usr/bin/env python 

import sys
import os
import time
import optparse
import StringIO
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from datetime import datetime
import cPickle
import inspect
import httplib
from collections import namedtuple
from multiprocessing import Pool
from api_functions import *
from fetch_functions import *

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Get user details',\
                usage = usage)
    parser.add_option('--authfile', action = 'store',\
        help = 'Authentication details file')
    parser.add_option('--user', action = 'store',\
        help = 'User whose information has to be fetched')
    return parser

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    api_info = create_api_objects(options.authfile)
    tweets = list()
    if options.user.isdigit():
        userinfo = lookup_user(api_info, user_id = int(options.user))
    else:
        userinfo = lookup_user(api_info, screen_name = options.user)
    print userinfo
    if options.user.isdigit():
        followers, friends = user_connections(api_info,\
                                user_id = int(options.user))
    else:
        followers, friends = user_connections(api_info,\
                                screen_name = options.user)
    print followers, friends

if __name__ == '__main__':
    main()
