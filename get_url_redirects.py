import sys
import os
import json
import StringIO
import urllib2
import argparse
from multiprocessing import Pool
from urlredirects import *
from utils import *
from datetime import datetime
import inspect
from threading import Thread
import math

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_args():
    parser = argparse.ArgumentParser(description = 'Identify\
        redirects in posts made by users on Twitter ')
    parser.add_argument('--data_dir', required = True,\
        help = 'User data files')
    parser.add_argument('--num_workers', default = 10, type = int,\
        help = 'Number of worker processes to spawn')
    return parser.parse_args()
     
def get_resolved_urls(linksfilename):
    resolved_urls = set()
    if os.path.exists(linksfilename):
        linksfile = open(linksfilename, 'r')
        for line in linksfile:
            splitline = line.strip().split('\t')
            baseURL = splitline[1]
            resolved_urls.add(baseURL)
        linksfile.close()
    return resolved_urls

def handle_outcome(outcome, success, baseURL, linksfile, contentDir):
    if success:
        filecontents = StringIO.StringIO()
        filecontents.write(outcome.urlhandle.read())
        filecontents.seek(0)
        md5 = hashlib.md5()
        md5.update(filecontents.getvalue())
        md5sum = md5.hexdigest()
        linksfile.write(json.dumps(datetime.now(),\
            default = datehandler) + '\t' +\
            baseURL + '\t' +\
            json.dumps(success) + '\t' +\
            str(outcome.redirects) + '\t' + \
            md5sum + '\n')
        contentfile = open(os.path.join(contentDir,\
            md5sum), 'w')
        contentfile.write(filecontents.getvalue())
        contentfile.close()
    else:
        linksfile.write(json.dumps(datetime.now(),\
            default = datehandler) + '\t' +\
            baseURL + '\t' +\
            json.dumps(success) + '\t' +\
            str(outcome) + '\n')

def resolve_redirects(user_id, data_dir):
    # create the file to which links will be saved and content of the
    # files will be saved
    print 'Resolving', user_id
    linksfilename = os.path.join(data_dir, str(user_id) + '.links')
    resolved_urls = get_resolved_urls(linksfilename)
    linksfile = open(linksfilename, 'a')
    datafilename = os.path.join(data_dir, str(user_id) + '.txt')
    contentDir = os.path.join(data_dir, str(user_id))
    if not os.path.exists(contentDir):
        os.mkdir(contentDir)
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
                baseURL = url['expanded_url']
            elif url['url']:
                baseURL = url['url']
            else:
                continue

            # Fix poorly formatted link
            if not baseURL.startswith('http://'):
                baseURL = 'http://' + baseURL
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
            handle_outcome(outcome, success, baseURL, linksfile, contentDir)
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
        for user_id in self.user_ids:
            try: 
                resolve_redirects(user_id, self.data_dir)
            except:
                print sys.exc_info()
                print >>self.failfile, user_id

# could return less than n chunks
def chunks(l, n):
    a = int(math.ceil(len(l) / float(n)))
    for i in xrange(0, len(l), a):
        yield l[i:i+a]

def main():
    args = get_args()
    filenames = os.listdir(args.data_dir)
    count = 0
    total = len(filenames)

    user_ids = list()
    for filename in filenames:
        count = count + 1
        if filename.endswith('.txt'):
            user_id = int(filename.split('.')[0])
            user_ids.append(user_id)

    sublist_generator = chunks(user_ids, args.num_workers)
    workerThreads = list()
    for i in xrange(args.num_workers):
        try:
            workerThread = ResolveURLThread(sublist_generator.next(),\
                args.data_dir)
        except StopIteration:
            break
        workerThread.start()
        workerThreads.append(workerThread)

    for workerThread in workerThreads:
        workerThread.join()

if __name__ == '__main__':
    main()
