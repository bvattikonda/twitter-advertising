#!/usr/bin/env python

# Identify the accounts that use any of the marketing tools

import sys
import datetime
import string
import optparse
import os
import json
import ast
from urlparse import urlparse
from collections import defaultdict
from HTMLParser import HTMLParser
from analysis import *

class HREFParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.linktext = None
    
    def handle_data(self, data):
        self.linktext = data

def marketing_user(data_dir, user_id, tools):
    userfile = open(os.path.join(data_dir, str(user_id) + '.txt'))
    try:
        userfile.readline()
        userfile.readline()
        userfile.readline()
    except:
        return False
    while True:
        line = userfile.readline()
        if not len(line):
            break
        tweet = json.loads(line)
        source_string = tweet['source']
        if '</a>' in source_string:
            parser = HREFParser()
            parser.feed(source_string)
            source = parser.linktext.strip()
            if source in tools:
                return True
    return False

def accounts_using_tools(data_dir, users, tools):
    marketing_users = 0
    total_users = len(users)
    for user in users:
        if marketing_user(data_dir, user, tools):
            marketing_users += 1
    return marketing_users / float(total_users)

def setup_parser():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'How many accounts\
            use marketing tools to send Tweets', usage = usage)
    parser.add_option('-s', help = 'Sponsored Tweets users')
    parser.add_option('-a', help = 'Adly users')
    parser.add_option('-w', help = 'Warrior Forums users')
    parser.add_option('--data_dir', help = 'Data directory')
    parser.add_option('-t', '--tools', help = 'File with list of tools that\
            can be uesd for social marketing')
    parser.add_option('--outfile', help = 'File to which output (if\
        any) has to be written')
    return parser
    
def correct_options(options):
    if not options.s or not options.a or not options.w or not\
        options.tools:
        return False

    if not options.data_dir or not os.path.exists(options.data_dir):
        return False
    return True

def main():
    parser = setup_parser()
    (options, args) = parser.parse_args()
    if not correct_options(options):
        parser.print_help()
        sys.exit(1)
    
    tools = set()
    for line in open(options.tools):
        tools.add(line.strip())

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)

    print accounts_using_tools(options.data_dir, fetched_adlyusers,
            tools) 
    print accounts_using_tools(options.data_dir, fetched_spntwusers,
            tools)
    print accounts_using_tools(options.data_dir, fetched_warriors,
            tools)
    
if __name__ == '__main__':
    main()
