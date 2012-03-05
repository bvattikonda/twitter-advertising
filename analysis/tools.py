#!/usr/bin/env python

# Identify the tools that advertisers use to send the Tweets

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

tools_usagefile = open('tools_usage.txt', 'w')
tools_per_profilefile = open('tools_per_profile.txt', 'w')

class HREFParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.linktext = None
    
    def handle_data(self, data):
        self.linktext = data

def get_tool_usage(data_dir, user_id):
    tool_usage = defaultdict(int) 
    userfile = open(os.path.join(data_dir, str(user_id) + '.txt'),
            'r')
    try:
        userfile.readline()
        userfile.readline()
        userfile.readline()
    except:
        return tool_usage

    while True:
        line = userfile.readline()
        if not len(line):
            break
        tweet = json.loads(line)
        source_string = tweet['source']
        if '</a>' in source_string:
            parser = HREFParser()
            parser.feed(source_string)
            source = parser.linktext
        else:
            source = source_string
        tool_usage[source] += 1
    return tool_usage

def sum_dicts(first, second):
    for key, value in first.iteritems():
        second[key] += value
    return second

def users_tools_usage(category, data_dir, users): 
    global_tool_usage = defaultdict(int)
    number_per_profile = list()
    for user_id in users:
        tool_usage = get_tool_usage(data_dir, user_id)
        number_per_profile.append(len(tool_usage))
        sum_dicts(tool_usage, global_tool_usage)

    for key, value in global_tool_usage.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf8', 'ignore')
        tools_usagefile.write(category + '\t' + str(key) + '\t' +\
                str(value) + '\n')

    for number in number_per_profile:
        tools_per_profilefile.write(category + '\t' + str(number) + '\n');

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)

    users_tools_usage('Adly', options.data_dir, fetched_adlyusers) 
    users_tools_usage('SpnTw', options.data_dir, fetched_spntwusers) 
    users_tools_usage('Warrior', options.data_dir, fetched_warriors) 

    tools_usagefile.close()
    tools_per_profilefile.close()

if __name__ == '__main__':
    main() 
