#!/usr/bin/env python 

import sys
import os
import optparse
import string
import time
import json
from collections import namedtuple
from datetime import datetime
import logging
from HTMLParser import HTMLParser
from utils import *
from api_functions import *
from fetch_functions import *

class User(object):
    def __init__(self, user_id = -1, screen_name = None, warrior_id =\
        None):
        self.user_id = user_id
        self.screen_name = screen_name 
        self.warrior_id = warrior_id 

class WarriorUserParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.screen_names = set()
        self.twitter_table = False
        self.twitter_account = False

    def handle_starttag(self, tag, attrs):
        if self.twitter_table and tag == 'dd':
            self.twitter_account = True 
            self.twitter_table = False
        return

    def handle_endtag(self, tag, attrs):
        return

    def handle_data(self, data):
        if data == 'Twitter':
            self.twitter_table = True
        if self.twitter_account:
            if data.isalnum():
                self.screen_names.add(data)
            self.twitter_account = False
        return
    def handle_startendtag(self, tag, attrs):
        return
    def handle_endtag(self, tag):
        return

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Twitter information\
        of Warrior Forums users',\
        usage = usage)
    parser.add_option('--data_dir', action = 'store',\
        help = 'Raw data directory')
    parser.add_option('--authfile', action = 'store',\
        help = 'Authentication details file')
    return parser

def correct_options(options):
    if not options.data_dir or not options.authfile:
        return False
    if not os.path.exists(options.data_dir) or not\
        os.path.exists(options.authfile):
        return False
    return True

def load_resolved_users(data_dir):
    resolved_usersfilename = os.path.join(data_dir, 'users.txt')
    if not os.path.exists(resolved_usersfilename):
        return set()

    resolved_usersfile = open(resolved_usersfilename)
    resolved_users = set()
    for line in resolved_usersfile:
        resolved_users.add(line.strip().split('\t')[2])
    return resolved_users

def analyze_warrior_data(options):
    # get warrior user ids which have been processed
    resolved_users = load_resolved_users(options.data_dir)

    # for each warrior user get information
    user_details = dict()
    warrior_pagenames = os.listdir(options.data_dir)
    for warrior_pagename in warrior_pagenames:
        if not warrior_pagename.endswith('.html'):
            continue
        warrior_id = warrior_pagename.replace('.html', '')
        if warrior_id in resolved_users:
            continue
        warriorpage = open(os.path.join(options.data_dir,
                        warrior_pagename))
        x = warriorpage.read().decode('utf8', 'ignore')
        parser = WarriorUserParser()
        parser.feed(x)
        for screen_name in parser.screen_names:
            if not len(screen_name) > 0:
                continue
            user_details[screen_name.lower()] = User(-1, screen_name,\
                                                warrior_id)
    # Users we do not have information about
    new_screen_names = list()
    for screen_name, user in user_details.iteritems():
        new_screen_names.append(screen_name)

    # Twitter API objects
    api_info = create_api_objects(options.authfile)

    # Fetch Twitter information and write to file
    outfile = open(os.path.join(options.data_dir, 'users.txt'), 'a')
    total = len(new_screen_names)
    count = 0
    logging.info('Fetching information of %d users' % total)
    while True:
        if count >= total:
            break
        current_screen_names = new_screen_names[count:count+min(100,\
                                total - count)]
        try:
            user_info_list = lookup_users(api_info,\
                                        screen_names =\
                                        current_screen_names)
        except Exception as e:
            count = count + 100
            logging.info(str(e))
            logging.info(str(current_screen_names))
            print e
            continue
        logging.info('Resolved %d of %d' %\
            (len(user_info_list), total))        
        for user_info in user_info_list:
            screen_name = user_info['screen_name'].decode('utf8')
            user_id = user_info['id']
            user_details[screen_name.lower()].user_id = user_id
            user_details[screen_name.lower()].\
                screen_name = screen_name
            outfile.write(str(user_id) + '\t' +\
                screen_name + '\t' +
                user_details[screen_name.lower()].warrior_id +\
                '\n')
        count = count + 100

    outfile.close()

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return
    logging.basicConfig(filename = os.path.join(options.data_dir,\
        'warrior_analysis.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)
    while True:
        logging.info('Begin analyzing data')
        start = time.time()
        analyze_warrior_data(options)
        end = time.time()
        logging.info('Run took %d minutes' % ((end - start) / 60))
        logging.info('End fetching data')
    
if __name__ == '__main__':
    if already_running(sys.argv[0]):
        print 'Already running'
        sys.exit(1)
    main()
