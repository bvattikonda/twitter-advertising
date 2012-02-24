#!/usr/bin/python
import oauth
from OpenSSL import SSL
import urlparse, time, webbrowser
from twisted.internet import ssl, reactor, protocol
from twisted.web import http

CONSUMER_KEY = 'R2gJ17R7NwsYrUf03t2EQ'
CONSUMER_SECRET = 'k2klKOTen6F9cZiLljeuA9TTG42ZispVbEcllzJvmVg'
ACCESS_KEY = '481417601-dQjvChTqDHnnGbMtTRYIWAXeHFASDtpmusqpX4tI'
ACCESS_SECRET = 'hVGrWES9oyVgAA5pvV734kgDLsN0HpFP2IHIzd1Pkg'
CONSUMER = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
ACCESS_TOKEN = oauth.OAuthToken(key = ACCESS_KEY, secret =
                ACCESS_SECRET)

ACCESS_TOKEN_FILE = 'OAUTH_ACCESS_TOKEN'

TWITTER_STREAM_API_HOST = 'stream.twitter.com'
TWITTER_STREAM_API_PATH = '/1/statuses/sample.json'

class TwitterStreamer(http.HTTPClient):
    def connectionMade(self):
        print self.factory.url
        self.sendCommand('GET', self.factory.url)
        self.sendHeader('Host', self.factory.host)
        self.sendHeader('User-Agent', self.factory.agent)
        self.sendHeader('Authorization', self.factory.oauth_header)
        self.endHeaders()
  
    def handleStatus(self, version, status, message):
        if status != '200':
            self.factory.tweetError(ValueError("bad status"))
  
    def lineReceived(self, line):
        self.factory.tweetReceived(line)

    def connectionLost(self, reason):
        self.factory.tweetError(reason)
        reactor.stop()

class TwitterStreamerFactory(protocol.ClientFactory):
    protocol = TwitterStreamer
    
    def __init__(self, oauth_header):
        self.url = TWITTER_STREAM_API_PATH
        self.agent='Twisted/TwitterStreamer'
        self.host = TWITTER_STREAM_API_HOST
        self.oauth_header = oauth_header
    
    def clientConnectionFailed(self, _, reason):
        self.tweetError(reason)
        reactor.stop()
    
    def tweetReceived(self, tweet):
        print tweet
    
    def tweetError(self, error):
        print error

class CtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        return ctx

def build_authorization_header(access_token):
    url = "https://%s%s" % (TWITTER_STREAM_API_HOST, TWITTER_STREAM_API_PATH)
    params = {
        'oauth_version': "1.0",
        'oauth_nonce': oauth.generate_nonce(),
        'oauth_timestamp': int(time.time()),
        'oauth_token': access_token.key,
        'oauth_consumer_key': CONSUMER.key
    }

    # Sign the request.
    req = oauth.OAuthRequest.from_consumer_and_token(\
                CONSUMER, http_url = url,\
                http_method = 'GET',\
                token = access_token,\
                parameters = {})
                
    req.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(), CONSUMER, access_token)

    # Grab the Authorization header
    header = req.to_header()['Authorization'].encode('utf-8')
    print "Authorization header:"
    print "     header = %s" % header
    return header

if __name__ == '__main__':
    # Build Authorization header from the access_token.
    auth_header = build_authorization_header(ACCESS_TOKEN)

    # Twitter stream using the Authorization header.
    twsf = TwitterStreamerFactory(auth_header)
    reactor.connectSSL(TWITTER_STREAM_API_HOST, 443, twsf,\
        CtxFactory())
    reactor.run()
