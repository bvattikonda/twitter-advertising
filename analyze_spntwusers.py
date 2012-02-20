#!/usr/bin/env python 

import sys
import os
import optparse
import json
from collections import namedtuple
import locale

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Analyze spntw\
        users',\
        usage = usage)
    parser.add_option('--users',\
        help = 'Text file with all the adly users information')
    return parser

def analyze_users(usersfilename):
    usersfile = open(usersfilename, 'r')
    for line in usersfile:
        x = json.loads(line.strip())
        if 'screen_name' in x:
            print x['screen_name']

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not options.users:
        parser.print_help()
        return
    analyze_users(options.users)

if __name__ == '__main__':
    main()
