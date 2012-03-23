#!/usr/bin/env python

import sys
import os
import cPickle
import json
import optparse
import logging
from collections import defaultdict
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from api_functions import *
from constants import *

# Identify the suspended users whose Tweets we have in the sample
# stream so that we do not have to fetch the links

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Identify suspended\
            users', usage = usage)
    parser.add_option('--authfile', action = 'store',\
        help = 'Authentication details file')
    parser.add_option('--stream_data', action = 'store',\
        help = 'Directory which has all the streaming data stored')
    return parser

def get_filename(stream_dir, count):
    filenames = os.listdir(stream_dir)
    for filename in filenames:
        if filename.startswith('sample_' + str(count) + '_'):
            return filename
    return None

def get_resolved(data_dir):
    filenames = os.listdir(data_dir)
    extracted = 0
    for filename in filenames:
        if filename.startswith('suspended_') and\
            filename.endswith('.users'):
            end = int(filename.split('.')[0].split('_')[-1])
            if extracted < end:
                extracted = end
    return extracted

def correct_options(options):
    if not options.stream_data or not options.authfile:
        return False
    if not os.path.exists(options.stream_data) or not\
        os.path.exists(options.authfile):
        return False
    return True
 
def get_users(current_file):
    users = set()
    while True:
        line = current_file.readline()
        if len(line) == 0:
            break
        tweet = json.loads(line)
        users.add(tweet['user']['id'])
    return users

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
        count += 100
    return active_users

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        sys.exit(1)

    api_info = create_api_objects(options.authfile)
    # set up logging
    logging.basicConfig(filename = os.path.join(options.stream_data,\
        'suspended_users.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)

    extracted = get_resolved(options.stream_data)
    logging.critical('Starting at %d' % (extracted))
    while True:
        filename = get_filename(options.stream_data, extracted)
        current_filename = os.path.join(options.stream_data,\
                filename)
        if not os.path.exists(current_filename):
            logging.critical('Finished extracting all existing files')
            break
        logging.info('Finding suspended users in %s' % (filename))
        begin = int(filename.replace('.tweets', '').split('_')[1])
        end = int(filename.replace('.tweets', '').split('_')[-1])
        suspended_filename = os.path.join(options.stream_data,\
                'suspended_' + str(begin) + '_' + str(end) + '.users')

        users = get_users(open(current_filename))
        active_users = get_active_users(api_info, users)
        suspended_users = users - active_users

        suspended_file = open(suspended_filename, 'w')
        for user_id in suspended_users:
            suspended_file.write(str(user_id) + '\n')
        extracted = end

if __name__ == '__main__':
    main()
