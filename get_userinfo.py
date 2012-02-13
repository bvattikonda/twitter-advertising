#!/usr/bin/env python 

import sys
import os
import time
import argparse
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

def get_args():
    parser = argparse.ArgumentParser(description = 'Get user details')
    parser.add_argument('--authfile', required = True,\
        help = 'File with all the authentication details of applications')
    parser.add_argument('--user', required = True,\
        help = 'User whose tweets have to be fetched')
    return parser.parse_args()

def main():
    args = get_args()
    api_info = create_api_objects(args.authfile)
    tweets = list()
    if args.user.isdigit():
        userinfo = lookup_user(api_info, user_id = int(args.user))
    else:
        userinfo = lookup_user(api_info, screen_name = args.user)
    print userinfo

if __name__ == '__main__':
    main()
