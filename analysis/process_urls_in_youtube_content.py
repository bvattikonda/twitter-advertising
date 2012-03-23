#!/usr/bin/env python

# Identify the domains in the text of YouTube video description

import sys
import os
from xml.etree.ElementTree import ElementTree
from urlparse import urlparse
from collections import defaultdict
from analysis import *

redirects_file = open('redirects_file.txt', 'w')

def sum_dicts(first, second):
    for key, value in first.iteritems():
        second[key] += value
    return second

def extract_domains(text):
    domains = defaultdict(int)
    splitline = text.strip().split()
    for item in splitline:
        if item.startswith('http'):
            try:
                parseResult = urlparse(item)
            except ValueError:
                continue
            domain = parseResult.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            if domain == 'bit.ly' or domain == 'ow.ly' or domain ==\
                'tinyurl.com':
                redirects_file.write(item.encode('utf8', 'ignore') + '\n')
                print item
            domains[domain] += 1
    return domains

def get_domains(videofile):
    tree = ElementTree()
    tree.parse(videofile)
    root = tree.getroot()
    children = list(root)
    for child in children:
        if child.tag == '{http://www.w3.org/2005/Atom}content':
            if not child.text:
                return defaultdict(int)
            return extract_domains(child.text.strip())

def analyze_videos(data_dir, outfilename):
    print outfilename
    filenames = os.listdir(data_dir)
    all_domains = defaultdict(int)
    total = len(filenames)
    count = 0
    for filename in filenames:
        if filename.endswith('.yt'):
            file = open(os.path.join(data_dir, filename), 'r')
            domains = get_domains(file)
            sum_dicts(domains, all_domains)
        count += 1
        if count % 1000 == 0:
            print count, total

    outfile = open(outfilename, 'w')
    for domain, count in all_domains.iteritems():
        outfile.write(domain.encode('utf8', 'ignore') + '\t' + str(count) + '\n')
    outfile.close()

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    analyze_videos(options.data_dir, options.outfile)

if __name__ == '__main__':
    main() 
