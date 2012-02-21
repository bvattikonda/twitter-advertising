#!/usr/bin/env python 

import sys
import os
import time
import optparse
import json
import StringIO
import logging
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

# Return the users who have been fetched in the past
def get_users(data_dir):
    nodename = os.uname()[1]
    id = int(nodename.replace('sysnet', '')) % 3
    user_ids = list()
    usersfilenames = os.listdir(data_dir)
    for userfilename in usersfilenames:
        lastmodified = os.stat(os.path.join(data_dir,\
                        userfilename)).st_mtime

        # only users who have not been updated in 12 hours
        if (lastmodified - time.time()) / 3600 < 12:
            continue

        if userfilename.endswith('.txt'):
            user_id = int(userfilename.split('.')[0])
            if user_id % 3 == id:
                user_ids.append(user_id)
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
    tweetsFound = False
    if user_infofile:
        user_info_buffer = StringIO.StringIO()
        try:
            user_info_buffer.write(user_infofile.readline())
            user_info_buffer.write(user_infofile.readline())
            user_info_buffer.write(user_infofile.readline())
            infoFound = True
        except:
            pass

    if not infoFound:
        user_info_buffer = StringIO.StringIO()
        # Try to fetch the relevant information
        user_info = lookup_user(api_info, user_id = user_id)
        
        # if failed to fetch, return
        if not user_info:
            logging.warning('User lookup failed %d' % (user_id))
            raise Exception('User lookup failed %d' % (user_id))
    
        logging.info(user_info['screen_name'])
        print user_info['screen_name']
        user_info_buffer.write(json.dumps(user_info) + '\n')
    
        followers, friends = user_connections(api_info, user_id = user_id)
        if followers == None or friends == None:
            logging.warning('User connections lookup failed %d' % (user_id))
            raise Exception('User connections lookup failed %d' % (user_id))
        user_info_buffer.write(json.dumps(followers) + '\n')
        user_info_buffer.write(json.dumps(friends) + '\n')
    else:
        logging.info('Information found for %d' % (user_id))
        line = user_infofile.readline()
        last_line = line
        if len(line) > 0:
            tweetsFound = True

        while len(line) > 0:
            user_info_buffer.write(line)
            last_line = line
            line = user_infofile.readline()
        last_tweet = json.loads(last_line)

    # get the latest user information and dump to pickle file
    if tweetsFound:
        logging.info('Tweets found for %d' % (user_id))
        tweets = get_new_user_tweets(api_info, user_id = user_id,
            since_id = last_tweet['id'])
    else:
        tweets = get_user_tweets(api_info, user_id = user_id)

    logging.info('%d tweets found for %d' % (len(tweets), user_id))
    for tweet in tweets:
        user_info_buffer.write(json.dumps(tweet) + '\n')
    return user_info_buffer

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Update user details',\
        usage = usage)
    parser.add_option('--data_dir', action = 'store',\
        help = 'Data directory')
    parser.add_option('--authfile', action = 'store',\
        help = 'Authentication details file')
    return parser

def correct_options(options):
    if not options.data_dir or not options.authfile:
        return False
    if not os.path.exists(options.data_dir):
        return False
    if not os.path.exists(options.authfile):
        return False
    return True

def update_userinfo(api_info, options):
    # Get users for whom we seek information
    user_ids = get_users(options.data_dir)
    logging.info('Updating info for %d users' % len(user_ids))

    for user_id in user_ids:
        try:
            user_info = get_user_info(options.data_dir, api_info, user_id) 
            if not user_info:
                continue
            userfilename = os.path.join(options.data_dir,\
                            str(user_id) + '.txt')
            userfile = open(userfilename, 'w')
            userfile.write(user_info.getvalue())
            userfile.close()
        except KeyboardInterrupt:
            logging.warning('KeyboardInterrupt, exiting')
            raise    
        except:
            print 'FATAL:', user_id, sys.exc_info()

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    api_info = create_api_objects(options.authfile)
    logging.basicConfig(filename = os.path.join(options.data_dir,\
        'update_streams_%s.log' % os.uname()[1]),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)

    while True:
        logging.info('Begin updating info')
        start = time.time()
        update_userinfo(api_info, options)
        end = time.time()
        logging.info('End updating info')
        if (end - start) < 600:
            time.sleep(600)

if __name__ == '__main__':
    main()
