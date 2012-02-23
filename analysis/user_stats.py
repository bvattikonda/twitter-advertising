#!/usr/bin/env python 

# Different user statistics

import sys
import os
import simplejson as json
import time
import ast
import optparse
from datetime import datetime
from analysis import *

def print_stats(adlyusers, spntwusers, warriors):
    print 'Adly:', len(adlyusers)
    print 'SpnTw:', len(spntwusers)
    print 'WarriorForums:', len(warriors)
    print 'Adly & SpnTw:', len(adlyusers & spntwusers)
    print 'Adly & WarriorForums:', len(adlyusers & warriors)
    print 'Adly & SpnTw:', len(spntwusers & warriors)
    print 'All:', len(adlyusers & spntwusers & warriors)

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    print '--- Users'
    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    print_stats(adlyusers, spntwusers, warriors)

    print '--- Users for whom Tweets have been fetched'
    fetched_adlyusers = fetched(adlyusers, '.txt', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.txt', options.data_dir)
    fetched_warriors = fetched(warriors, '.txt', options.data_dir)
    print_stats(fetched_adlyusers, fetched_spntwusers,\
        fetched_warriors)

    f = open(options.outfile, 'w')
    for user in fetched_adlyusers:
        try:
            f.write('Adly' + '\t' + str(get_follower_count(user,\
                options.data_dir)) + '\n') 
        except:
            pass

    for user in fetched_spntwusers:
        try:
            f.write('SpnTw' + '\t' + str(get_follower_count(user,\
                options.data_dir)) + '\n') 
        except:
            pass

    for user in fetched_warriors:
        try:
            f.write('Warrior' + '\t' + str(get_follower_count(user,\
                options.data_dir)) + '\n') 
        except:
            pass

    print '--- Users for whom links have been fetched'
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links',\
                            options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)
    print_stats(fetched_adlyusers, fetched_spntwusers,\
        fetched_warriors)

if __name__ == '__main__':
    main()
