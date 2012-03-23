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
    parser.add_option('--data_dir', action = 'store',\
        help = 'User data files')
    parser.add_option('--num_workers', default = 10, type = int,\
        help = 'Number of worker processes to spawn')
    return parser
     
def get_resolved_urls(linksfilename):
    resolved_urls = set()
    if os.path.exists(linksfilename):
        linksfile = open(linksfilename, 'r')
        for line in linksfile:
            splitline = line.strip().split('\t')
            try:
                baseURL = splitline[1]
            except IndexError:
                print line,
            resolved_urls.add(baseURL)
        linksfile.close()
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

def resolve_redirects(user_id, data_dir):
    # create the file to which links will be saved 
    linksfilename = os.path.join(data_dir, str(user_id) + '.links')
    if os.path.exists(linksfilename):
        return
    resolved_urls = get_resolved_urls(linksfilename)
    linksfile = open(linksfilename, 'a')
    datafilename = os.path.join(data_dir, str(user_id) + '.txt')
    datafile = open(datafilename, 'r')
    # ignore userinfo, friends and followers
    datafile.readline()
    datafile.readline()
    datafile.readline()
    line = datafile.readline().strip()
    while len(line) > 0:
        tweet = json.loads(line)
        for url in tweet['entities']['urls']:
            success = False
            # find baseURL
            if url['expanded_url']:
                baseURL = url['expanded_url'].strip()
            elif url['url']:
                baseURL = url['url'].strip()
            else:
                continue

            # Fix poorly formatted link
            baseURL = fixURL(baseURL)
            baseURL = fixURLEncoding(baseURL)
            if baseURL in resolved_urls:
                continue

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
                handle_outcome(outcome, success, baseURL, linksfile)
            except:
                pass
            resolved_urls.add(baseURL)
        line = datafile.readline().strip()

class ResolveURLThread(Thread):
    def __init__(self, user_ids, data_dir):
        Thread.__init__(self)
        self.user_ids = user_ids
        self.data_dir = data_dir
        self.failfile = open(os.path.join(data_dir, self.getName() +\
            '.fail'), 'w')
    
    def run(self):
        count = 0
        for user_id in self.user_ids:
            count = count + 1
            print '%d %d %d' % (user_id, count, len(self.user_ids))
            try:
                resolve_redirects(user_id, self.data_dir)
            except:
                print sys.exc_info()
                print >>self.failfile, user_id
        sys.exit()

# could return less than n chunks
def chunks(l, n):
    a = int(math.ceil(len(l) / float(n)))
    for i in xrange(0, len(l), a):
        yield l[i:i+a]

def correct_options(options):
    if not options.data_dir:
        return False
    if not os.path.exists(options.data_dir):
        return False
    return True

def get_users(options):
    data_dir = options.data_dir
    nodename = os.uname()[1]
    nodeid = int(nodename.replace('sysnet', '')) % 3
    user_ids = list()
    filenames = os.listdir(data_dir)
    for filename in filenames:
        if filename.endswith('.txt'):
            user_id = int(filename.split('.')[0])
            linksfilename = os.path.join(options.data_dir,\
                                str(user_id) + '.links')
            if os.path.exists(linksfilename):
                continue
            if user_id % 3 == nodeid:
                user_ids.append(user_id)
    return user_ids

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return

    user_ids = get_users(options)
    filenames = os.listdir(options.data_dir)

    nodename = os.uname()[1]
    nodeid = int(nodename.replace('sysnet', '')) % 3

    sublist_generator = chunks(user_ids, options.num_workers)
    workerThreads = list()
    for i in xrange(options.num_workers):
        try:
            workerThread = ResolveURLThread(sublist_generator.next(),\
                options.data_dir)
        except StopIteration:
            break
        workerThread.daemon = True
        workerThread.start()
        workerThreads.append(workerThread)

    while True:
        time.sleep(100)
        print 'Active threads:', threading.active_count()
        allExited = True
        for workerThread in workerThreads:
            if workerThread.isAlive():
                allExited = False
        if allExited:
            return

if __name__ == '__main__':
    main()
