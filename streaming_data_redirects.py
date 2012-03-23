#!/usr/bin/env python

import sys
import os
import time
import json
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
from telnetlib import Telnet

def get_job(server, port, task_id, path, pattern):
    tn = Telnet()
    tn.open(server, port)
    tn.write(task_id + '\t' + path + '\t' + pattern)
    return tn.read_all()

def main():
    f = open('temp.txt', 'w')
    while True:
        job = get_job('sysnet82.sysnet.ucsd.edu', 9000,\
                'link_redirects',\
                '/mnt/bvattikonda/stream_data',\
                'links_.*\.links')
        time.sleep(2)
        print job 
        print >>f, job
    
if __name__ == '__main__':
    main()
