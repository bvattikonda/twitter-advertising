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
    picklefile = os.path.join(data_dir, 'initial_users.pickle')
    if os.path.exists(picklefile):
        root_users = cPickle.load(open(picklefile, 'rb'))
    else:
        root_users = defaultdict(set)

    interest_domains = ['adf.ly']
    for domain in interest_domains:
        page_count = 1
        while True:
            search_output, success = block_on_call(api_info, 'search',\
                q = domain, 
                rpp = 100,
                page = page_count,
                lang = 'en')
            if success:
                if len(root_users[domain]) >= count:
                    break
                for result in search_output['results']:
                    root_users[domain].add((result['from_user'],\
                        result['from_user_id']))
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

def get_resolved_users(data_dir):
    datafilename = os.path.join(data_dir, 'resolved_users.txt')
    if os.path.exists(datafilename):
        datafile = open(datafilename, 'r')
        resolved_users = list()
        for line in datafile:
            resolved_users.append(int(line.strip()))
        datafile.close()
        return resolved_users
    else:
        return list()

def get_suspended_users(data_dir):
    datafilename = os.path.join(data_dir, 'suspended_users.txt')
    if os.path.exists(datafilename):
        datafile = open(datafilename, 'r')
        suspended_users = list()
        for line in datafile:
            suspended_users.append(int(line.strip()))
        datafile.close()
        return suspended_users
    else:
        return list()

def user_data(api_info, user_id):
    cursor = -1
    followers = list()
    while True:
        output, success = block_on_call(api_info, 'followers_ids',\
                                        user_id = user_id, cursor = cursor)
        if isinstance(output, tuple):
            followers += output[0]['ids']
            cursor = output[1][1]
            if cursor == 0:
                break
        else:
            return None, None
        if not success:
            return None, None

    cursor = -1
    friends = list()
    while True:
        output, success = block_on_call(api_info, 'friends_ids',\
                                        user_id = user_id, cursor = cursor)
        if isinstance(output, tuple):
            friends += output[0]['ids']
            cursor = output[1][1]
            if cursor == 0:
                break
        else:
            return None, None
        if not success:
            return None, None

   
    return followers, friends

def update_data(api_info,\
    user_id,\
    resolved_users,\
    suspended_users,\
    connections_file,\
    resolved_usersfile,\
    suspended_usersfile):
    if user_id in resolved_users:
        return
    followers, friends = user_data(api_info, user_id)
    resolved_users.append(user_id)
    if followers == None or friends == None:
        suspended_users.append(user_id)
        suspended_usersfile.write(str(user_id) + '\n')
    else:
        connections_file.write(str(user_id))
        connections_file.write('-' + str(followers))
        connections_file.write('-' + str(friends))
        connections_file.write('\n')
    resolved_usersfile.write(str(user_id) + '\n')

def flush_files(fileslist):
    for filep in fileslist:
        filep.flush()

def get_user_connections(user_id, connections_filename):
    connections_file = open(connections_filename, 'r')
    for line in connections_file:
        splitline = line.strip().split('-')
        fetched_userid = int(splitline[0])
        if user_id == fetched_userid:
            followers = ast.literal_eval(splitline[1])
            friends = ast.literal_eval(splitline[2])
            connections_file.close()
            return followers, friends
    connections_file.close()
    raise Exception('User information not fetched before %d' % (user_id))
    return None, None

def connected_users(api_info,\
    root_users,\
    connections_filename,\
    resolved_users,\
    suspended_users,\
    connections_file,\
    resolved_usersfile,\
    suspended_usersfile):

    print str(datetime.now()), 'Fetching information for depth 0'
    for screen_name, user_id in root_users:
        update_data(api_info, user_id,\
            resolved_users, suspended_users,\
            connections_file, resolved_usersfile, suspended_usersfile)

    print str(datetime.now()), 'Fetching information for depth 1'
    for screen_name, user_id in root_users:
        followers, friends = get_user_connections(user_id, connections_filename)
        count = 0
        for follower_id in followers:
            update_data(api_info, follower_id,\
                resolved_users, suspended_users,\
                connections_file, resolved_usersfile, suspended_usersfile)
            count = count + 1
            if count == 1000:
                flush_files([connections_file, resolved_usersfile,\
                    suspended_usersfile])
                break
        count = 0
        for friend_id in friends:
            update_data(api_info, follower_id,\
                resolved_users, suspended_users,\
                connections_file, resolved_usersfile, suspended_usersfile)
            count = count + 1
            if count == 1000:
                flush_files([connections_file, resolved_usersfile,\
                    suspended_usersfile])
                break
            
    print str(datetime.now()), 'Fetching information for depth 2'
    for screen_name, user_id in root_users:
        followers, friends = get_user_connections(user_id, connections_filename)
        for connection_id in followers + friends:
            if connection_id in resolved_users and connection_id not in\
                suspended_users:
                count = 0
                connection_followers, connection_friends =\
                    get_user_connections(connection_id, connections_filename)
                for follower_id in connection_followers:
                    update_data(api_info, follower_id,\
                        resolved_users, suspended_users,\
                        connections_file, resolved_usersfile,\
                        suspended_usersfile)
                    count = count + 1
                    if count == 1000:
                        flush_files([connections_file, resolved_usersfile,\
                            suspended_usersfile])
                        break
                count = 0
                for friend_id in connection_friends:
                    update_data(api_info, friend_id,\
                        resolved_users, suspended_users,\
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
    suspended_users = get_suspended_users(args.data_dir)

    connections_file = open(os.path.join(args.data_dir, 'connections.txt'), 'a')
    resolved_usersfile = open(os.path.join(args.data_dir, 'resolved_users.txt'), 'a')
    suspended_usersfile = open(os.path.join(args.data_dir, 'suspended_users.txt'), 'a')

    for domain in root_users:
        try:
            connected_users(api_info, root_users[domain],\
                os.path.join(args.data_dir, 'connections.txt'),\
                resolved_users, suspended_users,\
                connections_file, resolved_usersfile, suspended_usersfile)
        except:
            print datetime.now(), sys.exc_info()
            flush_files([connections_file, resolved_usersfile,\
                suspended_usersfile])
            sys.exit(1)

if __name__ == '__main__':
    main()
