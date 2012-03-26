#!/usr/bin/env python

import urllib
import urllib2
import urlparse
from urlredirects import *
from utils import *
from threading import Thread
import logging

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

class ResolveRedirectsThread(Thread):
    def __init__(self, outcomes, links_to_resolve):
        Thread.__init__(self)
        self.outcomes = outcomes
        self.links_to_resolve = links_to_resolve
    
    def run(self):
        logging.info('Starting thread')
        count = 0
        while True:
            success = False
            baseURL = self.links_to_resolve.get()
            baseURL = fixURL(baseURL)
            baseURL = fixURLEncoding(baseURL)

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

            self.outcomes.put((outcome, success, baseURL))
            count = count + 1
            self.links_to_resolve.task_done()
        logging.info('Thread: Resolved %d links' % (count))
