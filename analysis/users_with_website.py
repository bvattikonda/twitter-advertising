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

def user_has_website(user_id, data_dir):
    userfile = open(os.path.join(data_dir,\
        str(user_id) + '.txt'), 'r')
    try:
        userinfo = json.loads(userfile.readline().strip())
    except ValueError:
        return False
    if userinfo['url']:
        return True
    return False

def get_www_users(user_ids, data_dir):
    www_users = set()
    for user_id in user_ids:
        if user_has_website(user_id, data_dir):
            www_users.add(user_id)
    return www_users

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.txt', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.txt', options.data_dir)
    fetched_warriors = fetched(warriors, '.txt', options.data_dir)

    www_adlyusers = get_www_users(fetched_adlyusers, options.data_dir)
    www_spntwusers = get_www_users(fetched_spntwusers,\
                        options.data_dir)
    www_warriors = get_www_users(fetched_warriors, options.data_dir)

    print '--- Users who have websites'
    print 'Adly:\n%d\t%d\t%.2f' % (len(www_adlyusers),\
        len(fetched_adlyusers),\
        len(www_adlyusers) / float(len(fetched_adlyusers)))
    print 'SpnTw:\n%d\t%d\t%.2f' % (len(www_spntwusers),\
        len(fetched_spntwusers),len(www_spntwusers) /\
        float(len(fetched_spntwusers)))
    print 'Warrior:\n%d\t%d\t%.2f' % (len(www_warriors),\
        len(fetched_warriors),\
        len(www_warriors) / float(len(fetched_warriors)))

if __name__ == '__main__':
    main()
