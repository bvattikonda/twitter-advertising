#!/usr/bin/env python 

# ad networks: jol.ly, spn.tw, adby.me

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from datetime import datetime
import cPickle
import inspect

class Listener(StreamListener):
    def __init__(self, pickle_dir, api = None):
        super(Listener, self).__init__(api) 
        self.received_so_far = 0
        self.written_to_disk = 0
        self.unwritten = []
        self.pickle_dir = pickle_dir
        pickle_files = os.listdir(pickle_dir)
        for pickle_file in pickle_files:
            written_to_file = int(pickle_file.split('_')[2])
            if self.written_to_disk < written_to_file:
                self.written_to_disk = written_to_file

    def on_status(self, status):
        self.unwritten.append(status) 
        self.received_so_far = self.received_so_far + 1
        if self.received_so_far >= 1000:
            # dump the data collected so far
            pickle_filename = "sample_" +\
                str(self.written_to_disk) + "_" +\
                str(self.written_to_disk + 1000)
            cPickle.dump(self.unwritten, open(os.path.join(self.pickle_dir,\
                pickle_filename), 'wb'), 2)
            self.unwritten = []
            self.received_so_far = 0
            self.written_to_disk = self.written_to_disk + 1000
            print datetime.now(), pickle_filename
        return

    def on_delete(self, status_id, user_id):
        return

    def on_limit(self, track):
        print 'on_limit'
        sys.exit(1)
        return

    def on_error(self, status_code):
        print 'error occurred:', code
        sys.exit(1)

    def on_timeout(self):
        print 'Connection lost'
        sys.exit(1)

def main():
    auth = OAuthHandler('mNUFIRmx1PwY3kUGqEPUw',\
        '6d4RJvbxVqrOhGpQNzclD6atB0Y26fO4RNAc3RNFi5E')
    auth.set_access_token('419021038-yGdNfxAWQ3YNHf81N8bjFvrFdLvfBzpE8YuNVF8z',\
        '03QjioFrZcE6XGBOTMJVYXQZBWJMXPlrFaPZkngzrF4')

    api = API(auth)

    streamer = Listener(sys.argv[1], api)
    stream = Stream(auth, streamer)

#   stream.sample()
    stream.filter(track = ['#ad', 'sponsored', 'advertisement',\
        'Ad:', 'Advertisement', 'Ad'])
    return

if __name__ == '__main__':
    main()
