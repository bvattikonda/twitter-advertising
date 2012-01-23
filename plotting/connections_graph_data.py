#!/usr/bin/env python 

# Generate the data file from connections so that we can use GUESS to plot the
# connections graph

import sys
import os
import ast
import argparse

def get_args():
    parser = argparse.ArgumentParser(description = 'Get unique followers\
        for root users')
    parser.add_argument('--connections', required = True,\
        help = 'Text file describing the connections of users')
    parser.add_argument('--outfile', required = True,\
        help = 'File to which the data file has to be written')
    return parser.parse_args()

def write_nodedefs(connectionsfilename, outfile):
    outfile.write('nodedef> name\n')
    connectionsfile = open(connectionsfilename, 'r')
    nodes = set()
    for line in connectionsfile:
        splitline = line.strip().split('-')
        followers = ast.literal_eval(splitline[1])
        if len(followers) >= 2000:
            nodes.add(int(splitline[0]))
    connectionsfile.close()
    for node in nodes:
        outfile.write('n' + str(node) + '\n')
    return nodes

def write_edgedefs(nodes, connectionsfilename, outfile):
    outfile.write('edgedef> node1, node2, directed\n')
    connectionsfile = open(connectionsfilename, 'r')
    for line in connectionsfile:
        splitline = line.strip().split('-')
        try:
            node_id = int(splitline[0])
            if node_id not in nodes:
                continue
            followers = ast.literal_eval(splitline[1])
            for follower_id in followers:
                if follower_id in nodes:
                    outfile.write('n' + str(node_id) + ',' +\
                        'n' + str(follower_id) + ',' + 'true' + '\n')
        except IndexError:
            break

def main():
    args = get_args()
    outfile = open(args.outfile, 'w')
    nodes = write_nodedefs(args.connections, outfile)
    write_edgedefs(nodes, args.connections, outfile)

if __name__ == '__main__':
    main()
