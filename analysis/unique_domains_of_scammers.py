#!/usr/bin/env python

# Script to give data on the number of followers that the scammers have in our
# dataset

import sys
import datetime
import string
import argparse
from urlparse import urlparse
import os
import time
import json
import ast
from analysis import *

def get_domain(url):
    parseresult = urlparse(url)
    return parseresult.netloc

def get_plot_data(links_dir):
    plot_data = list()
    linksfilenames = os.listdir(links_dir)
    for linksfilename in linksfilenames:
        linksfile = open(os.path.join(links_dir, linksfilename), 'r')
        scammer = False
        unique_domains = set()
        for line in linksfile:
            if 'clickbank.net' in line:
                scammer = True
            splitline = line.strip().split('\t')
            success = json.loads(splitline[2])
            if success:
                redirect_list = ast.literal_eval(splitline[3])
                if len(redirect_list) == 0:
                    domain = get_domain(splitline[1])
                else:
                    domain = get_domain(redirect_list[-1][1])
                unique_domains.add(domain.lower())
        if scammer:
            print linksfilename, unique_domains
            plot_data.append(len(unique_domains))

    return plot_data

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return
    args = get_args()    
    plot_data = get_plot_data(args.links_dir)
    print len(plot_data)
    f = open('temp.txt', 'w')
    for item in plot_data:
        print >>f, item

if __name__ == '__main__':
    main()
