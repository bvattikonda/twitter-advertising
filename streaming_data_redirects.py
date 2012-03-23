#!/usr/bin/env python

import os, json, optparse 
from Queue import Queue
from telnetlib import Telnet
from resolve_redirects import ResolveRedirectsThread

def get_job(server, port, task_id, path, pattern):
    tn = Telnet()
    tn.open(server, port)
    tn.write(task_id + '\t' + path + '\t' + pattern)
    return tn.read_all()

def parse_args():
    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(description = 'Resolve redirects',\
                usage = usage)
    parser.add_option('--num_workers', default = 10, type = int,\
        help = 'Number of worker threads to spawn')
    return parser 

def execute_job(num_workers, linksfilename):
    links_to_resolve = Queue()
    suspended_usersfilename = linksfilename.replace('.links',\
            '.users').replace('links_', 'suspended_')
    linksfile = open(os.path.join('/mnt/bvattikonda/stream_data',
                linksfilename))
    suspended_usersfile = open(os.path.join('/mnt/bvattikonda/stream_data',
                suspended_usersfilename))
    suspended_users = set()
    for line in suspended_usersfile:
        suspended_users.add(int(line.strip()))
    
    logging.info('%d suspended users in %s' % (len(suspended_users),\
                linksfilename))

    for line in linksfile:
        tweet_id, user_id_str, url = line.split('\t')
        user_id = json.loads(user_id_str)
        if user_id in suspended_users:
            continue
        links_to_resolve.put(url, True)
    logging.info('%d links to be resolved' %\
            (links_to_resolve.qsize()))

    for i in xrange(num_workers):
        thread = ResolveRedirectsThread(links_to_resolve)
        thread.start()

    links_to_resolve.join()
    logging.info('Resolved all URLs in %s' % (linksfilename))

def main():
    parser = parse_args()

    logging.basicConfig(filename =\
            os.path.join('/mnt/bvattikonda/stream_data',\
                'redirects.log'),\
            format = '%(asctime)s - %(levelname)s - %(message)s',\
            level = logging.DEBUG)

    while True:
        job = get_job('sysnet82.sysnet.ucsd.edu', 9000,\
                'link_redirects',\
                '/mnt/bvattikonda/stream_data',\
                'links_.*\.links')
        logging.info('Resolving links in %s' % (job))
        execute_job(job)
    
if __name__ == '__main__':
    main()
