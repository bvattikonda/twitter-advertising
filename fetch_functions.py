import sys
import os
from api_functions import *
import cPickle
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))

def lookup_user(api_info, screen_name = None, user_id = None):
    user_info_list = list()
    success = False
    if screen_name:
        user_info_list, success = block_on_call(api_info, 'lookup_users',\
            screen_names = [screen_name])
    elif user_id:
        user_info_list, success = block_on_call(api_info, 'lookup_users',\
            user_ids = [user_id])
    if success:
        return user_info_list[0]
    return None

def get_new_user_tweets(api_info,\
    user_id = None,\
    screen_name = None,\
    since_id = None):
    new_tweets = list()
    if not since_id:
        return new_tweets

    while True:
        if screen_name:
            tweets, success = block_on_call(api_info, 'user_timeline',\
                screen_name = screen_name,\
                include_rts = 'true',\
                trim_user = 'true',
                include_entities = 'true')
        elif user_id:
            tweets, success = block_on_call(api_info, 'user_timeline',\
                screen_name = screen_name,\
                include_rts = 'true',\
                trim_user = 'true',
                include_entities = 'true')
        else:
            return new_tweets
        
        if success:
            tweets.reverse()
            new_tweets.extend(tweets)
            if len(tweets) < 200:
                return new_tweets

def get_user_tweets(api_info, user_id = None, screen_name = None):
    if not user_id and screen_name:
        userinfo = lookup_user(api_info, screen_name = screen_name)
        user_id = userinfo['id'] 

    all_tweets = list()
    tweets, success = block_on_call(api_info, 'user_timeline',\
        id = user_id,\
        count = 200,\
        include_rts = 'true',\
        trim_user = 'true',\
        include_entities = 'true')
    if not success:
        return None

    all_tweets.extend(tweets)
    if len(tweets) < 200:
        all_tweets.reverse()
        return all_tweets

    while True:
        print '\t', user_id, len(all_tweets)
        tweets, success = block_on_call(api_info, 'user_timeline',\
            id = user_id,\
            count = 200,\
            max_id = tweets[-1]['id'] + 1,\
            include_rts = 'true',\
            trim_user = 'true',\
            include_entities = 'true')
        if not success:
            return None

        all_tweets.extend(tweets)
        if len(tweets) < 200:
            all_tweets.reverse()
            return all_tweets

def user_connections(api_info, user_id = None, screen_name = None, max_followers = 0, max_friends = 0):
    cursor = -1
    followers = list()
    while True:
        if screen_name:
            output, success = block_on_call(api_info, 'followers_ids',\
                                            screen_name = screen_name, cursor = cursor)
        elif user_id:
            output, success = block_on_call(api_info, 'followers_ids',\
                                            user_id = user_id, cursor = cursor)
        if isinstance(output, tuple):
            followers += output[0]['ids']
            cursor = output[1][1]
            if cursor == 0:
                break
            if max_followers > 0 and len(followers) >= max_followers:
                break
        else:
            return None, None
        if not success:
            return None, None

    cursor = -1
    friends = list()
    while True:
        if screen_name:
            output, success = block_on_call(api_info, 'friends_ids',\
                                            screen_name = screen_name, cursor = cursor)
        elif user_id:
            output, success = block_on_call(api_info, 'friends_ids',\
                                            user_id = user_id, cursor = cursor)
        if isinstance(output, tuple):
            friends += output[0]['ids']
            cursor = output[1][1]
            if cursor == 0:
                break
            if max_friends > 0 and len(friends) > max_friends:
                break
        else:
            return None, None
        if not success:
            return None, None

    return followers, friends
