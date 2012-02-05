#!/usr/bin/env python 

import sys
import os
import argparse
import simplejson as json
from collections import namedtuple
import locale

def get_args():
    parser = argparse.ArgumentParser(description = 'Analyze adly users')
    parser.add_argument('--users', required = True,\
        help = 'Text file with all the adly users information')
    return parser.parse_args()

def analyze_users(usersfilename):
    usersfile = open(usersfilename, 'r')
    for line in usersfile:
        x = json.loads(line.strip())
        if 'screen_name' in x:
            print x['screen_name']

def main():
    args = get_args()
    analyze_users(args.users)

if __name__ == '__main__':
    main()
