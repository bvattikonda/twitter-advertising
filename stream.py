#!/usr/bin/env python 

from ssltwitterstream import *
import sys
import os
import time
import logging
import optparse
from utils import *

class Listener(TwitterStreamListener):
    def __init__(self, data_dir, tweets_per_file = 10000):
        self.parser = JSONParser()
        self.tweets_per_file = tweets_per_file
        # written to files and closed
        self.saved = 0
        # written to files but not closed
        self.unsaved = 0
        self.data_dir = data_dir 
        self.current_file = open(os.path.join(self.data_dir,\
            'sample' + '_' + str(self.saved) + '_' +\
            str(self.saved + self.tweets_per_file) + '.tweets'), 'w')
        self.start_time = time.time()
        self.local_start = self.start_time
        self.max_rate = 0

    def print_rate(self):
        current_time = time.time()
        global_rate = self.saved /\
                        (current_time - self.start_time) 
        local_rate = self.tweets_per_file /\
                        (current_time - self.local_start)
        self.local_start = time.time()
        if local_rate > self.max_rate:
            self.max_rate = local_rate
        logging.info('Avg: %.2f Current: %.2f Max: %.2f' %\
            (global_rate, local_rate, self.max_rate))

        print 'Avg: %.2f Current: %.2f Max: %.2f' %\
            (global_rate, local_rate, self.max_rate)

    def tweetReceived(self, tweet):
        self.unsaved += 1
        self.current_file.write(str(tweet) + '\n')
        if self.unsaved == self.tweets_per_file:
            self.unsaved = 0
            self.saved += self.tweets_per_file 
            self.current_file.close()
            self.current_file = open(os.path.join(self.data_dir,\
                'sample' + '_' + str(self.saved) + '_' +\
                str(self.saved + self.tweets_per_file) +\
                '.tweets'), 'w')
            self.print_rate()
        return True

    def twitterWarning(self, code, message, percent_full):
        logging.warning('%s %s %s' % (code, message, percent_full))
    
    def connectionMade(self):
        logging.critical('(Re)Connected to the server')

    def connectionLost(self, reason):
        logging.critical('Connection loss: %s' % (reason))

def parse_args():
    parser = optparse.OptionParser(description = 'Stream data from\
        Twitter')
    parser.add_option('--data_dir', action = 'store',\
        help = 'Directory to which the stream data has to be saved')
    return parser

def correct_options(options):
    if not options.data_dir:
        return False
    if not os.path.exists(options.data_dir):
        return False
    return True

def main():
    auth = Auth('R2gJ17R7NwsYrUf03t2EQ',
            'k2klKOTen6F9cZiLljeuA9TTG42ZispVbEcllzJvmVg',
            '481417601-dQjvChTqDHnnGbMtTRYIWAXeHFASDtpmusqpX4tI',
            'hVGrWES9oyVgAA5pvV734kgDLsN0HpFP2IHIzd1Pkg')
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return
    logging.basicConfig(filename = os.path.join(options.data_dir,\
        'stream.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)
    # We can only use one API object for streaming Twitter data

    logging.critical('Begin streaming')
    listener = Listener(options.data_dir)
    stream = streaming.Stream(auth, listener)
    stream.sample(delimited = 'length', stall_warnings = 'true')

if __name__ == '__main__':
    try:
        main()
    except:
        logging.critical('End streaming')
        logging.critical('%s' % str(sys.exc_info()))
        raise
