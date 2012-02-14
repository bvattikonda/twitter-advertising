#!/usr/bin/env python

# Script to get data on number of unique domain links that the advertisers Tweet

import sys
import datetime
import string
import argparse
import os
import json
import ast
from urlparse import urlparse
from utils import *

def get_args():
    parser = argparse.ArgumentParser(description = 'Generate earnings graph')
    parser.add_argument('--extension', default = '.png',\
        help = 'File format in which graphs are wanted (eps or png)')
    parser.add_argument('--links_dir', required = True,\
        help = 'Directory which has links data')
    return parser.parse_args()

def get_domain(url):
    parseresult = urlparse(url)
    return parseresult.netloc
    
def get_plot_data(links_dir):
    plot_data = list()
    linksfilenames = os.listdir(links_dir)
    for linksfilename in linksfilenames:
        linksfile = open(os.path.join(links_dir, linksfilename), 'r')
        count = 0
        unique_domains = set()
        for line in linksfile:
            splitline = line.strip().split('\t')
            success = json.loads(splitline[2])
            if success:
                redirect_list = ast.literal_eval(splitline[3])
                if len(redirect_list) == 0:
                    domain = get_domain(splitline[1])
                else:
                    domain = get_domain(redirect_list[-1][1])
                unique_domains.add(domain.lower())
                count = count + 1
        if count < 100:
            continue
        plot_data.append(len(unique_domains))
    return plot_data

def main():
    args = get_args()    
    plot_data = get_plot_data(args.links_dir)
    print len(plot_data)
    f = open('temp.txt', 'w')
    for item in plot_data:
        print >>f, item

if __name__ == '__main__':
    main()