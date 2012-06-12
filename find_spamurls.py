#!/usr/bin/env python

import optparse
import os 
import json
from urlparse import urlparse
import glob
import ast

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Find spam URLs in\
            user tweet feed',
            usage = usage)
    parser.add_option('--data_dir', help = 'Directory with user data')
    parser.add_option('--outfile', help = 'File to which the bad URLs\
            must be saved')
    return parser

def correct_options(options):
    if not os.path.exists(options.data_dir):
        return False
    if os.path.exists(options.outfile):
        return False
    return True

def ignore_domain(domain):
    if domain.endswith('facebook.com'):
        return True
    if domain.endswith('twitter.com'):
        return True
    if domain.endswith('youtube.com'):
        return True
    if domain.endswith('youtu.be'):
        return True
    if domain.endswith('itunes.apple.com'):
        return True

def extract_spamurls(data_dir, outfile):
    linksfilename_pattern = data_dir + '/' + '*.links'
    linksfilenames = glob.glob(linksfilename_pattern)
    for linksfilename in linksfilenames:
        linksfile = open(linksfilename)
        for line in linksfile:
            splitline = line.strip().split('\t')
            try:
                success = json.loads(splitline[2])
            except:
                print linksfilename, line
                continue

            if not success:
                continue
            try:
                redirect_list = ast.literal_eval(splitline[3])
            except:
                print linksfilename, line
                continue
            user_id = int(os.path.basename(linksfilename).replace('.links', ''))
            destination = splitline[1]
            if len(redirect_list):
                destination = redirect_list[-1][1]
            clickbankLink = False
            for redirect in redirect_list:
                if 'clickbank.net' in redirect[1]:
                    clickbankLink = True
                    break
            if clickbankLink:
                if 'clickbank.net' not in destination:
                    outfile.write(json.dumps(user_id) +  '\t' +\
                            json.dumps(destination.decode('utf8',
                                    'ignore')) + '\n')
            #domain =  urlparse(destination).netloc.lower()
            #if ignore_domain(domain):
            #    continue
            #outfile.write(json.dumps(user_id) +  '\t' +\
            #        json.dumps(destination.decode('utf8', 'ignore')) + '\n')
    
def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return
    extract_spamurls(options.data_dir, open(options.outfile, 'w')) 

if __name__ == '__main__':
    main()
