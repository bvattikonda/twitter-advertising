#!/usr/bin/env python 

import os
import sys
import cPickle
import inspect
import urlparse
import re
import unicodedata
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *

def sum_int_dicts(first, second):
    for key, value in second.iteritems():
        first[key] += value
    return first
