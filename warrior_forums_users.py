#!/usr/bin/env python
import sys
import os
import time
import json
import StringIO
import socket
import urllib
import urllib2
import urlparse
import httplib
import optparse 
import logging
from urlredirects import *
from utils import *
from datetime import datetime
import inspect
from threading import Thread
import math
from HTMLParser import HTMLParser

class WarriorForumParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.member_locations = set()
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr_name, attr_value in attrs:
                if 'warriorforum.com/members' in attr_value:
                    self.member_locations.add(attr_value)
        return

    def handle_endtag(self, tag, attrs):
        return
    def handle_data(self, data):
        return
    def handle_startendtag(self, tag, attrs):
        return
    def handle_endtag(self, tag):
        return

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Fetch Twitter\
        information of Warrior Forums users',\
        usage = usage)
    parser.add_option('--data_dir', action = 'store',\
        help = 'Directory to which the user information has to be\
        saved')
    return parser

def correct_options(options):
    if not options.data_dir or not os.path.exists(options.data_dir):
        return False
    return True

def load_fetched_users(data_dir):
    fetched_usersfilename = os.path.join(data_dir,\
        'fetched_users.txt')

    if not os.path.exists(fetched_usersfilename):
        return set()

    fetched_usersfile = open(fetched_usersfilename, 'r')
    fetched_users = set()
    for line in fetched_usersfile:
        fetched_users.add(line.strip().split()[0])
    fetched_usersfile.close()
    return fetched_users

def update_member_locations(data_dir, member_locations):
    member_locationsfile = open(os.path.join(data_dir,
                            'member_locations.txt'), 'r+')
    old_member_locations = set()
    for line in member_locationsfile:
        old_member_locations.add(line.strip())
    for member_location in member_locations:
        if member_location not in old_member_locations:
            member_locationsfile.write(member_location + '\n')
    member_locationsfile.close()
    return old_member_locations | member_locations
    
def fetch_users(options):
    users_fetched = load_fetched_users(options.data_dir)

    # connect to warrior forums
    conn = httplib.HTTPConnection('www.warriorforum.com')
    conn.connect()

    # get and save main page
    conn.request('GET', '/')
    resp = conn.getresponse()
    mainpage = resp.read()
    md5sum = md5_for_string(mainpage)
    f = open(os.path.join(options.data_dir, 'main_' + md5sum), 'w')
    f.write(mainpage)

    # get user page locations from the main page
    parser = WarriorForumParser()
    parser.feed(mainpage)
    member_locations = update_member_locations(options.data_dir, parser.member_locations)

    # fetch user page, save and record that the file has been saved
    fetched_usersfile = open(os.path.join(options.data_dir,
                            'fetched_users.txt'), 'a')
    for member_location in member_locations:
        parsestring = urlparse.urlparse(member_location)
        member_id = parsestring.path.split('/')[-1]\
                        .replace('.html', '')
        if member_id in users_fetched:
            continue

        conn.request('GET', parsestring.path)
        resp = conn.getresponse()
        page = resp.read()
        member_file = open(os.path.join(options.data_dir,\
                        member_id + '.html'), 'w')
        member_file.write(page)
        member_file.close()
        users_fetched.add(member_id)
        fetched_usersfile.write(member_id + '\n')
    fetched_usersfile.close()

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
    logging.basicConfig(filename = os.path.join(options.data_dir,\
        'warrior.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)
    while True:
        logging.info('Begin fetching data')
        start = datetime.now()
        fetch_users(options)
        end = datetime.now()
        logging.info('Run took %d minutes' % total_mins(start, end))
        logging.info('End fetching data')
        time.sleep(3600)

if __name__ == '__main__':
    if already_running(sys.argv[0]):
        print 'Already running'
        sys.exit(1)
    main()
