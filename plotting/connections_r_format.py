#!/usr/bin/env python 

# Generate data file from connections so that we can use R to analyze the
# connections graph, in particular we are looking for followers graph

import sys
import os 
import ast 
import argparse
import cPickle
import inspect

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_args():
    parser = argparse.ArgumentParser(description = 'Process connections data\
        for analysis in R')
    parser.add_argument('--root_users', required = True,\
        help = 'Text file which has the list of root users')
    parser.add_argument('--connections', required = True,\
        help = 'Text file describing the connections of users')
    parser.add_argument('--outfile', required = True,\
        help = 'File to which the data file has to be written')
    parser.add_argument('--index', required = True,\
        help = 'File to which the index of vertices should be written')
    return parser.parse_args()

def load_root_users(root_usersfilename):
    root_usersfile = open(root_usersfilename, 'r')
    root_users = set()
    for line in root_usersfile:
        root_users.add(int(line.strip()))
    return root_users

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

def create_edge_list(root_users, connectionsfilename, outfilename,\
    indexfilename):
    outfile = open(outfilename, 'w')
    # Graph vertices list so that vertices are numbered from 0 to |V|
    graph_vertices = list()
    for user in root_users:
        graph_vertices.append(user)

    for user_id in root_users:
        start_vertex = graph_vertices.index(user_id)
        try:
            followers, friends = get_user_connections(user_id,\
                connectionsfilename)
        except Exception as e:
            print e.message
            continue
        for follower in followers:
            if follower not in graph_vertices:
                graph_vertices.append(follower)
            end_vertex = graph_vertices.index(follower)
            outfile.write(str(start_vertex) + ' ' + str(end_vertex) + '\n')
    
    indexfile = open(indexfilename, 'w')
    index = 0
    for vertex in graph_vertices:           
        indexfile.write(str(index) + ' ' + str(vertex) + '\n')
        index += 1
    indexfile.close()
    outfile.close()

def main():
    args = get_args()
    root_users = load_root_users(args.root_users)
    create_edge_list(root_users, args.connections, args.outfile, args.index)

if __name__ == '__main__':
    main()
