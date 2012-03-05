#!/usr/bin/env python

# Identify the number of users who are affiliates

import sys
import datetime
import string
import optparse
import os
import json
import ast
from urlparse import urlparse
from analysis import *

def affiliate_domain(domain):
    if 'clickbank.net' in domain:
        return True
    if 'clickbank.com' in domain:
        return True
    if 'cbfeed.com' in domain:
        return True
    if 'rsscb.com' in domain:
        return True
    return False

    if domain == 'www.amzn.to':
        return True
    if domain == 'amzn.to':
        return True
    if domain == 'www.amazon.com':
        return True
    if domain == 'amazon.com':
        return True
    return False

def affiliate(user_id, data_dir):
    linksfile = open(os.path.join(data_dir,\
        str(user_id) + '.links'), 'r')
    for line in linksfile:
        splitline = line.strip().split('\t')
        try:
            success = json.loads(splitline[2])
        except:
            print user_id, line
            continue
        if success:
            try:
                redirect_list = ast.literal_eval(splitline[3])
            except:
                print user_id, line
                continue
            baseURL = splitline[1]
            domain = get_domain(baseURL)
            if affiliate_domain(domain):
                return True
            if len(redirect_list):
                domain = get_domain(redirect_list[-1][1])
                if affiliate_domain(domain):
                    return True
    return False

def get_a_users(user_ids, data_dir):
    a_users = set()
    for user_id in user_ids:
        if affiliate(user_id, data_dir):
            a_users.add(user_id)
    return a_users

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

    a_adlyusers = get_a_users(fetched_adlyusers, options.data_dir)
    a_spntwusers = get_a_users(fetched_spntwusers,\
                        options.data_dir)
    a_warriors = get_a_users(fetched_warriors, options.data_dir)

    print '--- Users who advertise Amazon'
    print 'Adly:\n%d\t%d\t%.2f' % (len(a_adlyusers),\
        len(fetched_adlyusers),\
        len(a_adlyusers) / float(len(fetched_adlyusers)))
    print 'SpnTw:\n%d\t%d\t%.2f' % (len(a_spntwusers),\
        len(fetched_spntwusers),len(a_spntwusers) /\
        float(len(fetched_spntwusers)))
    print 'Warrior:\n%d\t%d\t%.2f' % (len(a_warriors),\
        len(fetched_warriors),\
        len(a_warriors) / float(len(fetched_warriors)))

    f = open(options.outfile, 'w')
    for user in a_adlyusers:
        try:
            f.write('Adly' + '\t' + str(user) + '\t' +\
                str(get_follower_count(user, options.data_dir)) +\
                '\n')
        except:
            pass

    for user in a_spntwusers:
        try:
            f.write('SpnTw' + '\t' + str(user) + '\t' +\
                    str(get_follower_count(user, options.data_dir)) +\
                    '\n')
        except:
            pass

    for user in a_warriors:
        try:
            f.write('Warrior' + '\t' + str(user) + '\t' +\
                    str(get_follower_count(user, options.data_dir)) +\
                    '\n')
        except:
            pass

if __name__ == '__main__':
    main() 
