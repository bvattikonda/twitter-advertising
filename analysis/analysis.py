#!/usr/bin/env python

import optparse
import os
import json
import ast
from urlparse import urlparse

def get_domain(url):
    parseresult = urlparse(url)
    domain = parseresult.netloc.lower()
    if domain.startswith('www.'):
        domain = domain.replace('www.', '')
    return domain

# @line is a line from the links file
# returns None if the answer cannot be determined correctly
def get_destination_domain(line):
    splitline = line.strip().split('\t')
    success = False
    try:
        success = json.loads(splitline[2])
    except:
        return None
    if not success:
        return None

    try:
        redirect_list = ast.literal_eval(splitline[3])
    except:
        return None

    baseURL = splitline[1]
    destination_domain = get_domain(baseURL)
    if len(redirect_list):
        destination_domain = get_domain(redirect_list[-1][1])
    return destination_domain

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'How many users of\
                each kind', usage = usage)
    parser.add_option('-s', help = 'Sponsored Tweets users')
    parser.add_option('-a', help = 'Adly users')
    parser.add_option('-w', help = 'Warrior Forums users')
    parser.add_option('--data_dir', help = 'Data directory')
    parser.add_option('--outfile', help = 'File to which output (if\
        any) has to be written')
    return parser

# Number of followers of the user
def get_follower_count(user_id, data_dir):
    userfile = open(os.path.join(data_dir, str(user_id) + '.txt'), 'r')
    user_info = json.loads(userfile.readline())
    return user_info['followers_count']

# Number of friends of the user
def get_friend_count(user_id, data_dir):
    userfile = open(os.path.join(data_dir, str(user_id) + '.txt'), 'r')
    user_info = json.loads(userfile.readline())
    return user_info['friends_count']
 
def correct_options(options):
    if not options.s or not options.a or not options.w or not\
        options.data_dir:
        return False
    if not os.path.exists(options.s):
        return False
    if not os.path.exists(options.a):
        return False
    if not os.path.exists(options.w):
        return False
    if not os.path.exists(options.data_dir):
        return False
    return True

def load_users(usersfilename):
    usersfile = open(usersfilename, 'r')
    user_ids = set()
    for line in usersfile:
        splitline = line.strip().split('\t')
        user_id = int(splitline[0])
        user_ids.add(user_id)
    return user_ids

def fetched(user_ids, extension, data_dir):
    fetched_userids = set()
    for user_id in user_ids:
        if os.path.exists(os.path.join(data_dir, str(user_id) +\
            extension)):
            fetched_userids.add(user_id)
    return fetched_userids
