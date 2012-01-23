#!/usr/bin/env python 

# Identify the unique number of followers that the root users have

import sys
import os
import ast
import argparse
from collections import defaultdict

def get_args():
    parser = argparse.ArgumentParser(description = 'Get unique followers\
        for root users')
    parser.add_argument('--initial_users', required = True,\
        help = 'Text file with the root users information')
    parser.add_argument('--connections', required = True,\
        help = 'Text file describing the connections of users')
    return parser.parse_args()

def get_root_users(initial_usersfilename):
    initial_usersfile = open(initial_usersfilename, 'r')
    root_users = defaultdict(set)
    for line in initial_usersfile:
        domain, user_id = line.strip().split('\t')
        root_users[domain].add(int(user_id))
    return root_users

def analyze_unique_followers(advertisers, connections_filename):
    total_followers = 0
    unique_followers = set()
    max_followers = 0
    min_followers = float('inf')
    max_user = 0
    min_user = 0
    user_count = 0
    connections_file = open(connections_filename, 'r')
    for line in connections_file:
        splitline = line.strip().split('-')
        try:
            user_id = int(splitline[0])
            if user_id in advertisers:
                user_count += 1 
                followers = set(ast.literal_eval(splitline[1]))
                total_followers += len(followers)
                unique_followers |= followers
                if len(followers) > max_followers:
                    max_followers = len(followers)
                    max_user = user_id
                if len(followers) < min_followers:
                    min_followers = len(followers)
                    min_user = user_id
        except IndexError:
            break
    connections_file.close()
    print len(unique_followers), total_followers, user_count
    print max_followers, max_user, min_followers, min_user
    
def main():
    args = get_args() 
    root_users = get_root_users(args.initial_users)
    analyze_unique_followers(root_users['adf.ly'], args.connections)
    
if __name__ == '__main__':
    main()
