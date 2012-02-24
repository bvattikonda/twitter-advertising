#!/usr/bin/env python 

import sys
import os
from datetime import datetime
import inspect
import json
import logging
import optparse
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from api_functions import *
from utils import *

class Listener(StreamListener):
    def __init__(self, data_dir, tweets_per_file = 1000, api = None):
        super(Listener, self).__init__(api) 
        self.tweets_per_file = tweets_per_file
        # written to files and closed
        self.saved = 0
        # written to files but not closed
        self.unsaved = 0
        self.data_dir = data_dir 
        self.current_file = open(os.path.join(self.data_dir,\
            'sample' + '_' + str(self.saved) + '_' +\
            str(self.saved + self.tweets_per_file) + '.tweets'), 'w')
        self.start_time = datetime.now()
        self.local_start = datetime.now()
        self.max_rate = 0

    def print_rate(self):
        current_time = datetime.now()
        global_rate = self.saved /\
                        total_mins(self.start_time, current_time)
        local_rate = self.tweets_per_file /\
                        total_mins(self.local_start, current_time)
        self.local_start = datetime.now()
        if local_rate > self.max_rate:
            self.max_rate = local_rate
        logging.info('Avg: %.2f Current: %.2f Max: %.2f' %\
            (global_rate, local_rate, self.max_rate))

        print 'Avg: %.2f Current: %.2f Max: %.2f' %\
            (global_rate, local_rate, self.max_rate)

    def on_data(self, data):
        if data.isdigit():
            return True
        if len(data) == 0:
            return True

        message = json.loads(data)
        if 'warning' in message:
            logging.warning(data)

        self.unsaved += 1
        self.current_file.write(data + '\n')
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

    def on_error(self, status_code):
        print 'error:', status_code
        sys.exit(1)

def parse_args():
    parser = optparse.OptionParser(description = 'Stream data from\
        Twitter')
    parser.add_option('--data_dir', action = 'store',\
        help = 'Directory to which the stream data has to be saved')
    parser.add_option('--authfile', action = 'store',\
        help = 'File with all the authentication details of applications')
    return parser

def correct_options(options):
    if not options.data_dir or not options.authfile:
        return False
    if not os.path.exists(options.data_dir):
        return False
    if not os.path.exists(options.authfile):
        return False
    return True

def main():
    parser = parse_args()
    options = parser.parse_args()[0]
    if not correct_options(options):
        parser.print_help()
        return
    api_info = create_api_objects(options.authfile)
    logging.basicConfig(filename = os.path.join(options.data_dir,\
        'stream.log'),\
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)
    # We can only use one API object for streaming Twitter data
    api = api_info[0]

    logging.critical('Begin streaming')
    streamer = Listener(options.data_dir,\
        api = api)
    stream = Stream(api.auth, streamer, secure = True)
    stream.sample()

if __name__ == '__main__':
    try:
        main()
    except:
        logging.critical('End streaming')
        logging.critical('%s' % str(sys.exc_info()))
        raise
