#!/usr/bin/env python 

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *
from datetime import datetime
import cPickle
import inspect
import httplib
from collections import namedtuple
from multiprocessing import Pool

RETRY_TIME = 10
BACKOFF_TIME = 600

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def dump_user_info(user_pickle_dir, user_info):
    cPickle.dump(user_info, open(os.path.join(user_pickle_dir,\
        str(user_info.id) + '.pickle'), 'wb'))

def get_available_api(api_info):
    while True:
        for api in api_info:
            try:
                if get_remaining_hits(api) > 20:
                    return api
            except error.TweepError as e:
                try:
                    if e.response.status == httplib.BAD_GATEWAY:
                        time.sleep(RETRY_TIME)
                        continue
                    elif e.response.status == httplib.SERVICE_UNAVAILABLE:
                        time.sleep(RETRY_TIME)
                        continue
                    elif e.response.status == httplib.INTERNAL_SERVER_ERROR:
                        time.sleep(RETRY_TIME)
                        continue
                    else:
                        raise
                except AttributeError:
                    print_members(e)
        time.sleep(BACKOFF_TIME)

def get_remaining_hits(api):
    return api.rate_limit_status()['remaining_hits']

def print_remaining_hits(api_info):
    for api in api_info:
        print 'Remaining hits:', get_remaining_hits(api)

def create_api_objects():
    application_info = {'adsenser' : {'consumer_key' : 'VQNV36Py0WiXT4jBiHFLfg',\
        'consumer_secret' : 'FCJBiILPzT6AIa7nbr4c2EMqtOklfWwBzFFmKO27y0',\
        'access_token' : '419021038-y6i3DWUwrT1zsv5W7FsnsnRNttsUtqOUfZe1aE2t',\
        'access_secret' : 'xFEjUtS5p3ufdxnI49ok12WwbfcJjlcOKuyEhxBm8M'},\
        'adsenser1' : {'consumer_key' : 'mNUFIRmx1PwY3kUGqEPUw',\
        'consumer_secret' : '6d4RJvbxVqrOhGpQNzclD6atB0Y26fO4RNAc3RNFi5E',\
        'access_token' : '419021038-yGdNfxAWQ3YNHf81N8bjFvrFdLvfBzpE8YuNVF8z',\
        'access_secret' : '03QjioFrZcE6XGBOTMJVYXQZBWJMXPlrFaPZkngzrF4'},
        'adsenser2' : {'consumer_key' : 'h8zX88MO5UHVXUfpeoCPlw',\
        'consumer_secret' : 'u1XchLEc2MAUjfYyhbYaYgMzBkaYiMaeVpgaPn2oBFQ',\
        'access_token' : '419021038-r7dAVEhcPfoqbuVDNFe6STZwcdmwWvyEIFKesZhD',\
        'access_secret' : '3Vu47GAWlz9PgYphR0tNNHdE7r0US53ZL8pU1gUzIc'}}
    api_info = []
    for name, credentials in application_info.items():
        auth = OAuthHandler(credentials['consumer_key'],\
            credentials['consumer_secret'])
        auth.set_access_token(credentials['access_token'],\
            credentials['access_secret'])
        api_info.append(API(auth))
    return api_info 

def get_users():
    user_ids = cPickle.load(open('advertisers1.pickle', 'rb'))
    return user_ids
    final_users = set()
    for i in xrange(1000):
        final_users.add(user_ids.pop())
    return final_users

def block_on_call(api_info, function_name, **kwargs):
    while True:
        api = get_available_api(api_info)
        function = getattr(api, function_name)
        try:
            output = function(**kwargs)
            return output, True
        except error.TweepError as e:
            try:
                if e.response.status == httplib.BAD_GATEWAY:
                    time.sleep(RETRY_TIME)
                    continue
                elif e.response.status == httplib.SERVICE_UNAVAILABLE:
                    time.sleep(RETRY_TIME)
                    continue
                elif e.response.status == httplib.INTERNAL_SERVER_ERROR:
                    time.sleep(RETRY_TIME)
                    continue
                else:
                    print 'FAILED:', function_name, kwargs
                    return None, False
            except AttributeError:
                print_members(e)

def get_old_tweets(api_info, user_info):
    if not user_info.tweets:
        tweets, success = block_on_call(api_info, 'user_timeline',\
            id = user_info.id,\
            count = 200,\
            include_rts = 'true',\
            trim_user = 'true',\
            include_entities = 'true')
        if not success:
            user_info.error = True
            user_info.suspended = True
            user_info.suspension_moment = time.time()
            return
        else:
            user_info.tweets.extend(tweets)

    while True:
        print '\t', user_info.screen_name, len(user_info.tweets)
        tweets, success = block_on_call(api_info, 'user_timeline',\
            id = user_info.id,\
            count = 200,\
            max_id = user_info.tweets[-1].id + 1,\
            include_rts = 'true',\
            trim_user = 'true',\
            include_entities = 'true')
        if not success:
            user_info.error = True
            user_info.suspended = True
            user_info.suspension_moment = time.time()
        else:
            user_info.tweets.extend(tweets)
        if len(tweets) < 200:
            user_info.tweets.reverse()
            return

def get_user_tweets(api_info, user_info):
    if user_info.fetch_history:
        get_old_tweets(api_info, user_info)
        user_info.fetch_history = False
        return

    while True:
        tweets, success = block_on_call(api_info, 'user_timeline',\
            id = user_info.id,\
            count = 200,\
            since_id = user_info.tweets[-1].id,\
            trim_user = 'true',\
            include_entities = 'true')
        if not success:
            user_info.error = True
            user_info.suspended = True
            user_info.suspension_moment = time.time()
            break
        else:
            tweets.reverse()
            user_info.tweets.extend(tweets)
            if len(tweets) < 200:
                break

def get_upto_date(api_info, user_info, user_pickle_dir):
    print 'Updating for', user_info.screen_name
    if not user_info.followers_fetched:
        followers_ids_list, success = block_on_call(api_info, 'followers_ids',\
            user_id = user_info.id)
        if not success:
            user_info.error = True
            user_info.suspended = True
            user_info.suspension_moment = time.time()
        else:
            user_info.followers_ids_list.extend(followers_ids_list)
        user_info.followers_fetched = True
        dump_user_info(user_pickle_dir, user_info)
        print '\tFollowers fetched', len(user_info.followers_ids_list)
    else:
        print '\tFollowers already fetched', len(user_info.followers_ids_list)

    if not user_info.friends_fetched:
        friends_ids_list, success = block_on_call(api_info, 'friends_ids',\
            user_id = user_info.id)
        if not success:
            user_info.error = True
            user_info.suspended = True
            user_info.suspension_moment = time.time()
        else:
            user_info.friends_ids_list.extend(friends_ids_list)
        user_info.friends_fetched = True
        dump_user_info(user_pickle_dir, user_info)
        print '\tFriends fetched', len(user_info.friends_ids_list)
    else:
        print '\tFriends already fetched', len(user_info.friends_ids_list)
    get_user_tweets(api_info, user_info) 
    print '\tTweets: ', len(user_info.tweets)
    user_info.fetch_history = False
    user_info.last_updated = time.time()
    dump_user_info(user_pickle_dir, user_info)

def load_user_info(user_pickle_dir, user_id):
    user_info = None
    if os.path.exists(os.path.join(user_pickle_dir, str(user_id) + '.pickle')):
        print user_id
        user_info = cPickle.load((open(os.path.join(user_pickle_dir,\
                str(user_id) + '.pickle'), 'rb')))
        return user_info
    return None

def lookup_user(api_info, user_id):
    user_info_list, success = block_on_call(api_info, 'lookup_users',\
        user_ids = [user_id])
    if success:
        return user_info_list[0]
    return None

def create_attributes(user_info):
    if not hasattr(user_info, 'tweets'):
        setattr(user_info, 'tweets', list())
    if not hasattr(user_info, 'followers_ids_list'):
        setattr(user_info, 'followers_ids_list', list())
    if not hasattr(user_info, 'followers_fetched'):
        setattr(user_info, 'followers_fetched', False)
    if not hasattr(user_info, 'friends_ids_list'):
        setattr(user_info, 'friends_ids_list', list())
    if not hasattr(user_info, 'friends_fetched'):
        setattr(user_info, 'friends_fetched', False)
    if not hasattr(user_info, 'fetch_history'):
        setattr(user_info, 'fetch_history', True)
    if not hasattr(user_info, 'last_updated'):
        setattr(user_info, 'last_updated', None)
    if not hasattr(user_info, 'suspended'):
        setattr(user_info, 'suspended', False)
    if not hasattr(user_info, 'suspension_moment'):
        setattr(user_info, 'suspension_moment', None)

def get_user_info(user_pickle_dir, api_info, user_id):
    # try to load old pickle file
    user_info = load_user_info(user_pickle_dir, user_id)

    # if not available, try to fetch the relevant information
    if not user_info:
        user_info = lookup_user(api_info, user_id)
    
    # if failed to fetch, return
    if not user_info:
        return

    # create attributes which are not available by default
    create_attributes(user_info)
    
    if user_info.suspended:
        return

    dump_user_info(user_pickle_dir, user_info)

    # get the latest user information and dump to pickle file
    get_upto_date(api_info, user_info, user_pickle_dir)
    
def main():
    user_pickle_dir = sys.argv[2]
    api_info = create_api_objects()
    print_remaining_hits(api_info)

    # Get users for whom we seek information
    user_ids = get_users()

    for user_id in user_ids:
        try:
            get_user_info(user_pickle_dir, api_info, user_id) 
        except:
            print 'FATAL:', user_id, sys.exc_info()

if __name__ == '__main__':
    main()
