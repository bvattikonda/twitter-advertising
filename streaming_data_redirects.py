#!/usr/bin/env python

import os, json, optparse, logging
from datetime import datetime
from Queue import Queue
from telnetlib import Telnet
from resolve_redirects import ResolveRedirectsThread
from utils import *

def get_job(server, port, task_id, path, pattern):
    tn = Telnet()
    tn.open(server, port)
    tn.write(task_id + '\t' + path + '\t' + pattern)
    return tn.read_all()

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Resolve redirects',\
                usage = usage)
    parser.add_option('--data_dir', action = 'store',\
        help = 'Directory containing links files')
    parser.add_option('--num_workers', default = 10, type = int,\
        help = 'Number of worker threads to spawn')
    return parser 

def handle_outcome(outcome, success, baseURL, outfile):
    printoutput = None
    if success:
        printoutput = str(outcome.redirects).strip()
    else:
        printoutput = str(outcome).strip()
    outfile.write(json.dumps(datetime.now(),\
        default = datehandler) + '\t' +\
        baseURL + '\t' +\
        json.dumps(success) + '\t' +\
        printoutput + '\n')

def execute_job(data_dir, num_workers, linksfilename):
    begin = int(linksfilename.replace('.links', '').split('_')[1])
    end = int(linksfilename.replace('.links', '').split('_')[-1])
    links_to_resolve = Queue()
    outcomes = Queue()
    suspended_usersfilename = 'suspended_' + str(begin) + '_' +\
                              str(end) + '.users'
    # open the input files and output file
    linksfile = open(os.path.join(data_dir, linksfilename))
    suspended_usersfile = open(os.path.join(data_dir,\
                suspended_usersfilename))
    outfilename = 'redirects_' + str(begin) + '_' +\
                  str(end) + '.redirects'
    if os.path.exists(os.path.join(data_dir, outfilename)):
        size = os.path.getsize(os.path.join(data_dir, outfilename))
        if size > 0:
            logging.critical('%s already resolved' % (linksfilename))
            return

    outfile = open(os.path.join(data_dir, outfilename), 'w')
    
    # read the list of suspended users, links tweeted by these users
    # can be ignored
    suspended_users = set()
    for line in suspended_usersfile:
        suspended_users.add(int(line.strip()))
    
    logging.info('%d suspended users in %s' % (len(suspended_users),\
                suspended_usersfilename))

    # read the links that have to be resolved
    links = set()
    for line in linksfile:
        tweet_id, user_id_str, url = line.strip().split('\t')
        user_id = json.loads(user_id_str)
        if user_id in suspended_users:
            continue
        links.add(url)

    to_resolve = 0
    for url in links:
        links_to_resolve.put(url, True)
        to_resolve += 1

    logging.info('%d links to be resolved' %\
            (links_to_resolve.qsize()))

    # start threads which resolve the URLs
    for i in xrange(num_workers):
        thread = ResolveRedirectsThread(outcomes, links_to_resolve)
        thread.daemon = True
        thread.start()

    # write output to file
    links_to_resolve.join()

    while not outcomes.empty():
        outcome, success, baseURL = outcomes.get()
        handle_outcome(outcome, success, baseURL, outfile)

    logging.info('Resolved all URLs in %s' % (linksfilename))

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    data_dir = options.data_dir
    nodename = os.uname()[1]

    logging.basicConfig(filename =\
            os.path.join(data_dir,\
                nodename + '_redirects.log'),\
            format = '%(asctime)s - %(levelname)s - %(message)s',\
            level = logging.DEBUG)

    logging.info('Begin logging')
    while True:
        job = get_job('sysnet82.sysnet.ucsd.edu', 9000,\
                'link_redirects',\
                data_dir,\
                'links_.*\.links')
        if len(job) == 0:
            break
        logging.info('Resolving links in %s' % (job))
        execute_job(data_dir, options.num_workers, job)
    logging.critical('Finished all jobs, exiting')
    
if __name__ == '__main__':
    main()
