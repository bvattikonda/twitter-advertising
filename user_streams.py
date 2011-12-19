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
    user_ids = cPickle.load(open('advertisers.pickle', 'rb'))
    return user_ids

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
                    print 'FATAL:', function_name, kwargs
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
            break
        else:
            tweets.reverse()
            user_info.tweets.extend(tweets)
            if len(tweets) < 200:
                break

def get_upto_date(api_info, user_info, user_pickle_dir):
    print 'Updating for', user_info.screen_name
    if not user_info.followers_fetched:
        followers_ids, success = block_on_call(api_info, 'followers_ids',\
            user_id = user_info.id)
        if not success:
            user_info.error = True
        else:
            user_info.followers_ids.extend(followers_ids)
        user_info.followers_fetched = True
        dump_user_info(user_pickle_dir, user_info)
        print '\tFollowers fetched', len(user_info.followers_ids)
    else:
        print '\tFollowers already fetched', len(user_info.followers_ids)

    if not user_info.friends_fetched:
        friends_ids, success = block_on_call(api_info, 'friends_ids',\
            user_id = user_info.id)
        if not success:
            user_info.error = True
        else:
            user_info.friends_ids.extend(friends_ids)
        user_info.friends_fetched = True
        dump_user_info(user_pickle_dir, user_info)
        print '\tFriends fetched', len(user_info.friends_ids)
    else:
        print '\tFriends already fetched', len(user_info.friends_ids)
    get_user_tweets(api_info, user_info) 
    print '\tTweets: ', len(user_info.tweets)
    user_info.fetch_history = False
    user_info.last_updated = time.time()
    dump_user_info(user_pickle_dir, user_info)

def load_user_infos(user_ids):
    pickle_dir = sys.argv[2]
    user_infos = list()
    new_user_ids = set()
    for user_id in user_ids:
        if os.path.exists(os.path.join(pickle_dir, str(user_id) + '.pickle')):
            print user_id
            user_infos.append(cPickle.load(open(os.path.join(pickle_dir,\
                str(user_id) + '.pickle'), 'rb')))
        else:
            new_user_ids.add(user_id)
    return user_infos, new_user_ids

def get_user_infos(api_info, new_user_ids):
    new_user_infos = list()
    current_users = list()
    current_users_count = 0
    for new_user_id in new_user_ids:
        current_users.append(new_user_id)
        current_users_count = current_users_count + 1
        if current_users_count == 100:
            current_user_infos, success = block_on_call(api_info, 'lookup_users',\
                user_ids = current_users)
            new_user_infos.extend(current_user_infos)
            current_users = list()
            current_users_count = 0

    if current_users_count != 0:
        print current_users
        current_user_infos, success = block_on_call(api_info, 'lookup_users',\
            user_ids = current_users)
        new_user_infos.extend(current_user_infos)
    
    print 'Basic user info fetched' 
    return new_user_infos

def create_attributes(user_infos):
    for user_info in user_infos:
        setattr(user_info, 'tweets', list())
        setattr(user_info, 'followers_ids', list())
        setattr(user_info, 'followers_fetched', False)
        setattr(user_info, 'friends_ids', list())
        setattr(user_info, 'friends_fetched', False)
        setattr(user_info, 'fetch_history', True)
        setattr(user_info, 'last_updated', None)

def main():
    user_pickle_dir = sys.argv[2]
    api_info = create_api_objects()
    print_remaining_hits(api_info)

    # Get users for whom we seek information
    user_ids = get_users()

    # Identify new users
    user_infos, new_user_ids = load_user_infos(user_ids)
    print 'Old:', len(user_infos), 'New:', len(new_user_ids)

    # Get basic information for the new users
    new_user_infos = get_user_infos(api_info, new_user_ids)

    # Create additional state information before saving to disk
    create_attributes(new_user_infos)
    for new_user_info in new_user_infos:
        dump_user_info(user_pickle_dir, new_user_info)
    user_infos.extend(new_user_infos)

    # For each user get missing information
    while True:
        if len(user_infos) == 0:
            break
        user_info = user_infos[0]
        setattr(user_info, 'error', False)
        get_upto_date(api_info, user_info, user_pickle_dir)
        user_infos.remove(user_info)

    sys.exit(1)

    while True:
        for user_info in user_infos:
            api = get_available_api(api_info)
            get_user_tweets(api, user_info)
            user_info.last_updated = time.time()
            cPickle.dump(user_info, open(os.path.join(user_pickle_dir,\
                str(user_info.id) + '.pickle'), 'wb'))

if __name__ == '__main__':
    main()
