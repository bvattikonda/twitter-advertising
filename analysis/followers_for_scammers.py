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

def get_follower_count(users_dir, user_id):
    userfile = open(os.path.join(users_dir, str(user_id) + '.txt'), 'r')
    userfile.readline()
    followers = json.loads(userfile.readline())
    print len(followers)
    return len(followers)
    
def get_plot_data(users_dir, links_dir):
    plot_data = list()
    linksfilenames = os.listdir(links_dir)
    for linksfilename in linksfilenames:
        linksfile = open(os.path.join(links_dir, linksfilename), 'r')
        for line in linksfile:
            if 'clickbank.net' in line:
                follower_count = get_follower_count(users_dir,
                    int(linksfilename.replace('.links', '')))
                plot_data.append(follower_count)
                break
    return plot_data

def main():
    args = get_args()    
    plot_data = get_plot_data(args.users_dir, args.links_dir)
    print len(plot_data)

if __name__ == '__main__':
    main()
