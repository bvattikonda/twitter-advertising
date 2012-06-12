#!/usr/bin/env python

# Identify properties of the accounts that have been suspended

import sys
import optparse
import os
import json
from datetime import datetime
import ast
import numpy
from collections import namedtuple
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    '..'))
import logging
from analysis import *

RedirectProperties = namedtuple('RedirectProperties', ['mean', 'std',\
        'min', 'max'])
begin_2011 = datetime(2011, 1, 1)
        
def correct_options(options):
    if not options.data_dir or not os.path.exists(options.data_dir)\
        or not options.outfile:
        return False
    if not options.a or not options.s or not options.w or not\
        options.outfile:
        return False
    return True

def setup_parser():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'What are the\
            properties of redirects employed by these marketers?',
            usage = usage)
    parser.add_option('-s', help = 'Sponsored Tweets users')
    parser.add_option('-a', help = 'Adly users')
    parser.add_option('-w', help = 'Warrior Forums users')
    parser.add_option('--data_dir', help = 'Data directory')
    parser.add_option('--outfile', help = 'File to which output (if\
        any) has to be written')
    return parser

def redirect_properties(data_dir, user_id):
    redirect_props = list()
    try:
        linksfile = open(os.path.join(data_dir, str(user_id) +\
                    '.links'))
    except IOError:
        return None
    for line in linksfile:
        try:
            date, baseURL, success_str, redirects = line.strip().split('\t')
            success = json.loads(success_str)
        except ValueError:
            continue
        if success:
            try:
                redirect_props.append(1 +\
                        len(ast.literal_eval(redirects)))
            except:
                print user_id, line
                pass
    if not redirect_props:
        return None
    return RedirectProperties(numpy.mean(redirect_props),\
            numpy.std(redirect_props), min(redirect_props),\
            max(redirect_props))

def main():
    parser = setup_parser()
    (options, args) = parser.parse_args()
    if not correct_options(options):
        parser.print_help()
        sys.exit(1)

    adlyusers = load_users(options.a)
    spntwusers = load_users(options.s)
    warriors = load_users(options.w)
    fetched_adlyusers = fetched(adlyusers, '.links', options.data_dir)
    fetched_spntwusers = fetched(spntwusers, '.links', options.data_dir)
    fetched_warriors = fetched(warriors, '.links', options.data_dir)
    
    outfile = open(options.outfile, 'w')
    for user_id in fetched_adlyusers:
        props = redirect_properties(options.data_dir, user_id)
        if props:
            outfile.write('\t'.join(['Adly'] + [str(x) for x in props]) + '\n')
    for user_id in fetched_spntwusers:
        props = redirect_properties(options.data_dir, user_id)
        if props:
            outfile.write('\t'.join(['SpnTw'] + [str(x) for x in props]) + '\n')
    for user_id in fetched_warriors:
        props = redirect_properties(options.data_dir, user_id)
        if props:
            outfile.write('\t'.join(['Warrior'] + [str(x) for x in props]) + '\n')
    outfile.close()

if __name__ == '__main__':
    main()
