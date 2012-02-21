#!/usr/bin/env python

# Identify the number of users who have websites

import sys
import datetime
import string
import optparse
import os
import json
import ast
from analysis import *

def user_redirects_through_google(user_id, data_dir):
    linksfile = open(os.path.join(data_dir,\
        str(user_id) + '.links'), 'r')
    for line in linksfile:
        splitline = line.strip().split('\t')
        try:
            success = json.loads(splitline[2])
        except:
            print user_id, line
            return False
        if success:
            try:
                redirect_list = ast.literal_eval(splitline[3])
            except:
                print user_id, line
                return False
            if not len(redirect_list):
                return False
            for item in redirect_list[:-1]:
                domain = get_domain(item[1])
                if domain == 'google.com':
                    return True
                if domain == 'www.google.com':
                    return True
    return False

def get_g_users(user_ids, data_dir):
    g_users = set()
    for user_id in user_ids:
        if user_redirects_through_google(user_id, data_dir):
            g_users.add(user_id)
    return g_users

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)

    g_adlyusers = get_g_users(fetched_adlyusers, options.data_dir)
    g_spntwusers = get_g_users(fetched_spntwusers,\
                        options.data_dir)
    g_warriors = get_g_users(fetched_warriors, options.data_dir)

    print '--- Users who redirect through Google'
    print 'Adly:\n%d\t%d\t%.2f' % (len(g_adlyusers),\
        len(fetched_adlyusers),\
        len(g_adlyusers) / float(len(fetched_adlyusers)))
    print 'SpnTw:\n%d\t%d\t%.2f' % (len(g_spntwusers),\
        len(fetched_spntwusers),len(g_spntwusers) /\
        float(len(fetched_spntwusers)))
    print 'Warrior:\n%d\t%d\t%.2f' % (len(g_warriors),\
        len(fetched_warriors),\
        len(g_warriors) / float(len(fetched_warriors)))

if __name__ == '__main__':
    main()
