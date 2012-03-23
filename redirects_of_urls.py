#!/usr/bin/env python

import sys
import os
import time
import json
import StringIO
import socket
import urllib
import urllib2
import urlparse
import httplib
import optparse 
from urlredirects import *
from utils import *
from datetime import datetime
import inspect
from threading import Thread
import threading
import math

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Get redirects',\
        usage = usage)
    parser.add_option('--inputfile', action = 'store',\
        help = 'File which has the URLs that need to be resolved')
    parser.add_option('--outfile', action = 'store',\
        help = 'File to which redirects have to be written')
    return parser
     
def get_resolved_urls(outfilename):
    resolved_urls = set()
    if os.path.exists(outfilename):
        outfile = open(outfilename, 'r')
        for line in outfile:
            splitline = line.strip().split('\t')
            try:
                baseURL = splitline[1]
            except IndexError:
                print line,
            resolved_urls.add(baseURL)
        outfile.close()
    return resolved_urls

def handle_outcome(outcome, success, baseURL, linksfile):
    printoutput = None
    if success:
        printoutput = str(outcome.redirects).strip()
    else:
        printoutput = str(outcome).strip()
    linksfile.write(json.dumps(datetime.now(),\
        default = datehandler) + '\t' +\
        baseURL + '\t' +\
        json.dumps(success) + '\t' +\
        printoutput + '\n')

def fixURL(baseURL):
    parseresult = urlparse.urlparse(baseURL) 
    if len(parseresult.scheme) == 0:
        baseURL = 'http://' + baseURL
        return baseURL
    return baseURL
   
def fixURLEncoding(baseURL):
    # turn string into unicode
    if not isinstance(baseURL,unicode):
        baseURL = baseURL.decode('utf8')

    # parse it
    parsed = urlparse.urlsplit(baseURL)

    # divide the netloc further
    userpass,at,hostport = parsed.netloc.partition('@')
    user,colon1,pass_ = userpass.partition(':')
    host,colon2,port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme.encode('utf8')
    user = urllib.quote(user.encode('utf8'))
    colon1 = colon1.encode('utf8')
    pass_ = urllib.quote(pass_.encode('utf8'))
    at = at.encode('utf8')
    host = host.encode('idna')
    colon2 = colon2.encode('utf8')
    port = port.encode('utf8')
    path = '/'.join(  # could be encoded slashes!
        urllib.quote(urllib.unquote(pce).encode('utf8'),'')
        for pce in parsed.path.split('/')
    )
    query = urllib.quote(urllib.unquote(parsed.query).\
                encode('utf8'),'=&?/')
    fragment = urllib.quote(urllib.unquote(parsed.fragment).\
                encode('utf8'))

    # put it back together
    netloc = ''.join((user,colon1,pass_,at,host,colon2,port))
    return urlparse.urlunsplit((scheme,netloc,path,query,fragment))

def resolve_redirects(resolved_urls, baseURL, outfile):
    success = False

    # Fix poorly formatted link
    baseURL = fixURL(baseURL)
    baseURL = fixURLEncoding(baseURL)
    if baseURL in resolved_urls:
        return

    # Get redirects and write to file
    try:
        outcome = get_redirects(baseURL)
        success = True
    except urllib2.HTTPError as e:
        outcome = (e.code, e.msg)
    except urllib2.URLError as e:
        if isinstance(e, str):
            outcome = redirects.reason
        else:
            outcome = e 

    except Exception as e:
        outcome = str(e)
    try:
        handle_outcome(outcome, success, baseURL, outfile)
    except:
        pass
    resolved_urls.add(baseURL)

def correct_options(options):
    if not options.inputfile:
        return False
    if not options.outfile:
        return False
    if not os.path.exists(options.inputfile):
        return False
    return True

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    resolved_urls = get_resolved_urls(options.outfile)
    inputfile = open(options.inputfile, 'r')
    outfile = open(options.outfile, 'a')
    count = 0
    for line in inputfile:
        print count, 'Resolving', line.strip()
        resolve_redirects(resolved_urls, line.strip(), outfile);
        outfile.flush()
        count += 1

if __name__ == '__main__':
    main()
