import sys
import os
import urllib2
import inspect
import argparse
import urlparse
import re
import cPickle
import cStringIO
import shutil
from multiprocessing import Pool
from constants import *
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_redirects(url):
    request = urllib2.Request(url)
    f = urllib2.urlopen(request)
    if hasattr(request, 'redirect_dict'):
        return url, request.redirect_dict
    else:
        return url, None

def get_links_to_follow(results_dir, user_info):
    links_followed = set()
    if os.path.exists(os.path.join(results_dir, 'links_followed.pickle')):
        links_followed = cPickle.load(open(os.path.join(results_dir,\
            'links_followed.pickle'), 'rb'))
    ad_links = set()
    for tweet in user_info.tweets:
        for url in tweet.entities['urls']:
            if url['expanded_url']:
                for ad_domain_pattern in ad_domain_patterns:
                    if re.match(ad_domain_pattern,\
                        urlparse.urlparse(url['expanded_url']).netloc)\
                        and 'adf.ly' not in url['expanded_url']\
                        and 'q.gs' not in url['expanded_url']\
                        and 'spn.sr' not in url['expanded_url']:
                        ad_links.add(url['expanded_url'])
    return ad_links - links_followed

def load_current_results(results_dir):
    links_followed = set()
    links_redirect_info = dict()
    if os.path.exists(os.path.join(results_dir, 'links_followed.pickle')):
        links_followed = cPickle.load(open(os.path.join(results_dir,\
            'links_followed.pickle'), 'rb'))
        shutil.copyfile(os.path.join(results_dir,\
            'links_followed.pickle'), os.path.join(results_dir,\
            'links_followed.pickle.backup'))
    if os.path.exists(os.path.join(results_dir, 'links_redirect_info.pickle')):
        links_redirect_info = cPickle.load(open(os.path.join(results_dir,\
            'links_redirect_info.pickle'), 'rb'))
        shutil.copyfile(os.path.join(results_dir,\
            'links_redirect_info.pickle'), os.path.join(results_dir,\
            'links_redirect_info.pickle.backup'))
    
    return links_followed, links_redirect_info

def update_results(results_dir, results):
    # Parse the current results
    links = set()
    link_redirects = dict()
    for url, redirect_dict in results:
        links.add(url)
        link_redirects[url] = redirect_dict
    
    # Update the master set of results
    links_followed, links_redirect_info = load_current_results(results_dir)
    links_followed |= links
    links_redirect_info.update(link_redirects)
    print type(links_followed)
    cPickle.dump(links_followed, open(os.path.join(results_dir,\
        'links_followed.pickle'), 'wb'))
    print type(links_redirect_info)
    cPickle.dump(links_redirect_info, open(os.path.join(results_dir,\
        'links_redirect_info.pickle'), 'wb'))

def get_args():
    parser = argparse.ArgumentParser(description = 'Identify redirects')
    parser.add_argument('--data_dir', required = True,\
        help = 'User data files')
    parser.add_argument('--num_workers', default = 10, type = int,\
        help = 'Number of worker processes to spawn')
    return parser.parse_args()
     
def redirects_of_user():
    

def main():
    args = get_args()
    pickle_files = os.listdir(args.pickle_dir)
    user_infos = list()
    links_followed = set()
    count = 0
    for pickle_filename in pickle_files:
        user_info = load_user_info(args.pickle_dir, pickle_filename)
        links_to_follow = get_links_to_follow(args.results_dir, user_info)
        print 'Following links from %s %d' %\
            (user_info.screen_name, user_info.id)
        pool = Pool(args.num_workers)
        results = pool.imap_unordered(get_redirects, links_to_follow)
        update_results(args.results_dir, results)
        pool.close()
        pool.join()
        count = count + 1
        if count == 200:
            break

if __name__ == '__main__':
    main()
