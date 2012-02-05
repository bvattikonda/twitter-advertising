#!/usr/bin/env python 

# Given multiple connections file, generate one file which has the union of all
# the information

import os
import sys
import argparse
import ast

def get_args():
    parser = argparse.ArgumentParser(description = 'Merge connections files')
    parser.add_argument('--input_files', required = True, nargs = '+',\
        help = 'Connection files that should be merged')
    parser.add_argument('--outfile', required = True,\
        help = 'File to which the merged connections should be written')
    return parser.parse_args()

def merge_files(inputfiles, outfile):
    written_users = set()
    for inputfile in inputfiles:
        for line in inputfile:
            user_id = int(line.strip().split('-')[0])
            if user_id in written_users:
                continue
            written_users.add(user_id)
            outfile.write(line)
        inputfile.close()
    outfile.close()
    
def main():
    args = get_args()
    merge_files([open(filename, 'r') for filename in args.input_files],\
        open(args.outfile, 'w'))

if __name__ == '__main__':
    main()
