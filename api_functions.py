import inspect
import time
import sys
import os
import httplib
from collections import defaultdict
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),\
    'tweepy'))
from tweepy import *

RETRY_TIME = 10

def print_members(element):
    for item in inspect.getmembers(element):
        print item

def get_remaining_hits(api):
    return api.rate_limit_status()['remaining_hits']

def print_remaining_hits(api_info):
    for api in api_info:
        print 'Remaining hits:', get_remaining_hits(api)

def get_available_api(api_info):
    BACKOFF_TIME = 60
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

def create_api_objects(authinfo_filename):
    authinfofile = open(authinfo_filename, 'r')
    application_info = defaultdict(dict)
    for line in authinfofile:
        splitline = line.strip().split('\t')
        account = splitline[0]
        consumer_secret = splitline[2]
        consumer_key = splitline[3]
        access_token = splitline[4]
        access_secret = splitline[5]
        application_info[account] = {'consumer_key': consumer_key,\
            'consumer_secret' : consumer_secret,\
            'access_token' : access_token,\
            'access_secret' : access_secret}
    api_info = list()
    for account, credentials in application_info.items():
        auth = OAuthHandler(credentials['consumer_key'],\
            credentials['consumer_secret'])
        auth.set_access_token(credentials['access_token'],\
            credentials['access_secret'])
        api_info.append(API(auth, parser = parsers.JSONParser()))
    return api_info 

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
