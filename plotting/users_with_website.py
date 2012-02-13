#!/usr/bin/env python

# Script to give data on the number of followers that the scammers have in our
# dataset

import sys
import datetime
import string
import argparse
import os
import json
import ast

def get_args():
    parser = argparse.ArgumentParser(description = 'Generate earnings graph')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--users_dir', required = True,\
        help = 'Directory which has user data')
    parser.add_argument('--links_dir', required = True,\
        help = 'Directory which has links data')
    return parser.parse_args()

def main():
    args = get_args()    
    filenames = os.listdir(args.links_dir)
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
