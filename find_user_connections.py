#!/usr/bin/env python 

# The goal of this script is to get the connections of people who are sending
# advertisements. We will start with a small set of advertisers, follow their
# followers upto a constant DEPTH.

import sys
import os
import ast
import cPickle
import argparse
from datetime import datetime
from collections import defaultdict
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from api_functions import *
from constants import *

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_root_users(api_info, count, data_dir):
    picklefile = os.path.join(data_dir, 'inital_users.pickle')
    if os.path.exists(picklefile):
        root_users = cPickle.load(open(picklefile, 'rb'))
    else:
        root_users = defaultdict(set)

    interest_domains = ['spn.tw', 'adf.ly']
    for domain in interest_domains:
        page_count = 1
        while True:
            results, success = block_on_call(api_info, 'search',\
                q = ad_domain, 
                rpp = 100,
                page = page_count)
            if success:
                if len(root_users[domain]) >= count:
                    break
                for result in results:
                    root_users[domain].add((result.from_user,\
                        result.from_user_id))
                page_count += 1
                if page_count == 15:
                    break
    cPickle.dump(root_users, open(picklefile, 'wb'))
    return root_users

def get_args():
    parser = argparse.ArgumentParser(description = 'Get user connectivity')
    parser.add_argument('--data_dir', required = True,\
        help = 'Directory from / to which all pickle files can be\
            loaded / stored')
    parser.add_argument('--authfile', required = True,\
        help = 'File with all the authentication details of applications')
    return parser.parse_args()

def get_resolved_users(data_dir):
    datafilename = os.path.join(data_dir, 'resolved_users.txt')
    if os.path.exists(datafilename):
        datafile = open(datafilename, 'r')
        resolved_users = list()
        for line in datafile:
            resolved_users.append(int(line.strip()))
        datafile.close()
        return set(resolved_users)
    else:
        return set()

def get_connections(data_dir):
    datafilename = os.path.join(data_dir, 'connections.txt')
    if os.path.exists(datafilename):
        connections = defaultdict(dict)
        datafile = open(os.path.join(data_dir, 'connections.txt'), 'r')
        for line in datafile:
            splitline = line.strip().split('-')
            user_id = int(splitline[0])
            followers = ast.literal_eval(splitline[1])
            friends = ast.literal_eval(splitline[2])
            connections[user_id]['Followers'] = followers
            connections[user_id]['Friends'] = friends
        return connections
    else:
        return defaultdict(dict)

def get_suspended_users(data_dir):
    datafilename = os.path.join(data_dir, 'suspended_users.txt')
    if os.path.exists(datafilename):
        datafile = open(datafilename, 'r')
        suspended_users = list()
        for line in datafile:
            suspended_users.append(int(line.strip()))
        datafile.close()
        return set(suspended_users)
    else:
        return set()

def user_data(api_info, user_id):
    followers_ids_list, success = block_on_call(api_info, 'followers_ids',\
                                    user_id = user_id)
    if not success:
        return None, None

    friends_ids_list, success = block_on_call(api_info, 'friends_ids',\
                                    user_id = user_id)
    if not success:
        return None, None
    
    return followers_ids_list, friends_ids_list

def update_data(api_info,\
    data_dir,\
    user_id,\
    connections,\
    resolved_users,\
    suspended_users,\
    connections_file,\
    resolved_usersfile,\
    suspended_usersfile):
    if user_id in resolved_users:
        return
    followers, friends = user_data(api_info, user_id)
    resolved_users.add(user_id)
    if followers == None or friends == None:
        suspended_users.add(user_id)
        suspended_usersfile.write(str(user_id) + '\n')
    else:
        connections[user_id]['Followers'] = followers
        connections[user_id]['Friends'] = friends
        connections_file.write(str(user_id))
        connections_file.write('-' + str(connections[user_id]['Followers']))
        connections_file.write('-' + str(connections[user_id]['Friends']))
        connections_file.write('\n')
    resolved_usersfile.write(str(user_id) + '\n')

def flush_files(fileslist):
    for filep in fileslist:
        filep.flush()

def connected_users(api_info,\
    data_dir,\
    root_users,\
    connections,\
    resolved_users,\
    suspended_users,\
    connections_file,\
    resolved_usersfile,\
    suspended_usersfile):

    print str(datetime.now()), 'Fetching information for depth 0'
    for screen_name, user_id in root_users:
        update_data(api_info, data_dir, user_id,\
            connections, resolved_users, suspended_users,\
            connections_file, resolved_usersfile, suspended_usersfile)

    print str(datetime.now()), 'Fetching information for depth 1'
    for screen_name, user_id in root_users:
        count = 0
        for follower_id in connections[user_id]['Followers']:
            update_data(api_info, data_dir, follower_id,\
                connections, resolved_users, suspended_users,\
                connections_file, resolved_usersfile, suspended_usersfile)
            count = count + 1
            if count == 1000:
                flush_files([connections_file, resolved_usersfile,\
                    suspended_usersfile])
                break
        count = 0
        for friend_id in connections[user_id]['Friends']:
            update_data(api_info, data_dir, follower_id,\
                connections, resolved_users, suspended_users,\
                connections_file, resolved_usersfile, suspended_usersfile)
            count = count + 1
            if count == 1000:
                flush_files([connections_file, resolved_usersfile,\
                    suspended_usersfile])
                break
            
    print str(datetime.now()), 'Fetching information for depth 2'
    for screen_name, user_id in root_users:
        for connection_id in connections[user_id]['Followers'] + \
            connections[user_id]['Friends']:
            if connection_id in connections:
                count = 0
                for follower_id in connections[user_id]['Followers']:
                    update_data(api_info, data_dir, follower_id,\
                        connections, resolved_users, suspended_users,\
                        connections_file, resolved_usersfile,\
                        suspended_usersfile)
                    count = count + 1
                    if count == 1000:
                        flush_files([connections_file, resolved_usersfile,\
                            suspended_usersfile])
                        break
                count = 0
                for friend_id in connections[user_id]['Friends']:
                    update_data(api_info, data_dir, friend_id,\
                        connections, resolved_users, suspended_users,\
                        connections_file, resolved_usersfile,\
                        suspended_usersfile)
                    count = count + 1
                    if count == 1000:
                        flush_files([connections_file, resolved_usersfile,\
                            suspended_usersfile])
                        break

def main():
    args = get_args()
    api_info = create_api_objects(args.authfile)
    print_remaining_hits(api_info)
    # Get bootstrapping users for each domain
    root_users = get_root_users(api_info, 100,\
        args.data_dir)

    resolved_users = get_resolved_users(args.data_dir)
    connections = get_connections(args.data_dir)
    suspended_users = get_suspended_users(args.data_dir)

    connections_file = open(os.path.join(args.data_dir, 'connections.txt'), 'a')
    resolved_usersfile = open(os.path.join(args.data_dir, 'resolved_users.txt'), 'a')
    suspended_usersfile = open(os.path.join(args.data_dir, 'suspended_users.txt'), 'a')

    for domain in root_users:
        try:
            connected_users(api_info, args.data_dir,\
                root_users[domain], connections, resolved_users,\
                suspended_users, connections_file, resolved_usersfile,\
                suspended_usersfile)
        except:
            flush_files([connections_file, resolved_usersfile,\
                suspended_usersfile])
            sys.exit(1)

if __name__ == '__main__':
    main()
