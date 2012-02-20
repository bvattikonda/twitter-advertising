#!/usr/bin/env python

# Script to give data on the number of followers that the scammers have in our
# dataset

import sys
import datetime
import string
import optparse
import os
import json
import ast

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Find users who have\
        a website mentioned in their profile',\
        usage = usage)
    parser.add_option('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_option('--data_dir',\
        help = 'Directory which has user data')
    return parser

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    filenames = os.listdir(options.links_dir)
    count = 0
    scammer_count = 0
    for filename in filenames:
        linksfile = open(os.path.join(args.links_dir,\
            filename), 'r')
        scammer = False
        for line in linksfile:
            if 'clickbank.net' in line:
                scammer = True
        if not scammer:
            continue
        scammer_count += 1
        userfile = open(os.path.join(args.users_dir,\
            filename.replace('.links', '') + '.txt'), 'r')
        userinfo = json.loads(userfile.readline().strip())
        if userinfo['url']:
            count += 1
    print count, scammer_count 
        
if __name__ == '__main__':
    main()
