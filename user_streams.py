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

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_users(usersfilename):
    user_ids = list()
    usersfile = open(usersfilename, 'r')
    for line in usersfile:
        user_ids.append(int(line.strip()))
    return user_ids

def load_user_info(data_dir, user_id):
    user_info = None
    user_info_filename = os.path.join(data_dir, str(user_id) + '.txt')
    if os.path.exists(user_info_filename):
        return open(user_info_filename, 'r')
    return None

def get_user_info(data_dir, api_info, user_id):
    user_infofile = load_user_info(data_dir, user_id)
    infoFound = False 
    if user_infofile:
        user_info_buffer = StringIO.StringIO()
        try:
            user_info_buffer.write(user_infofile.readline())
            user_info_buffer.write(user_infofile.readline())
            user_info_buffer.write(user_infofile.readline())
            infoFound = True
        except:
            user_info_buffer = StringIO.StringIO()
            pass

    if not infoFound:
        # Try to fetch the relevant information
        user_info = lookup_user(api_info, user_id = user_id)
        
        # if failed to fetch, return
        if not user_info:
            raise Exception('User lookup failed %d' % (user_id))
    
        print user_info['screen_name']
        user_info_buffer.write(str(user_info) + '\n')
    
        followers, friends = user_connections(api_info, user_id = user_id)
        if followers == None or friends == None:
            raise Exception('User connections lookup failed %d' % (user_id))
        user_info_buffer.write(str(followers) + '\n')
        user_info_buffer.write(str(friends) + '\n')
    else:
        print 'Information found for %d' % (user_id)

    # get the latest user information and dump to pickle file
    tweets = get_user_tweets(api_info, user_id = user_id)
    user_info_buffer.write(str(tweets) + '\n')
    return user_info_buffer
    
def get_args():
    parser = argparse.ArgumentParser(description = 'Get user details')
    parser.add_argument('--data_dir', required = True,\
        help = 'Directory to which the user info files can be stored')
    parser.add_argument('--authfile', required = True,\
        help = 'File with all the authentication details of applications')
    parser.add_argument('--users', required = True,\
        help = 'File with the users for whom information has to be fetched')
    return parser.parse_args()

def main():
    args = get_args()
    api_info = create_api_objects(args.authfile)
    print_remaining_hits(api_info)

    # Get users for whom we seek information
    user_ids = get_users(args.users)

    for user_id in user_ids:
        try:
            user_info = get_user_info(args.data_dir, api_info, user_id) 
            if not user_info:
                continue
            userfilename = os.path.join(args.data_dir, str(user_id) + '.txt')
            userfile = open(userfilename, 'w')
            userfile.write(user_info.getvalue())
            userfile.close()
        except:
            print 'FATAL:', user_id, sys.exc_info()

if __name__ == '__main__':
    main()
