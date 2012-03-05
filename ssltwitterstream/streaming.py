#!/usr/bin/python
from ssltwitterstream import oauth
from OpenSSL import SSL
import urlparse, time, webbrowser
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.ssl import ClientContextFactory
from twisted.web import http

TWITTER_STREAM_API_HOST = 'stream.twitter.com'

class TwitterStreamer(http.HTTPClient):
    def connectionMade(self):
        x = urlparse.urlunparse((None,
                None,
                self.factory.path,
                None,
                self.factory.query,
                None))
        self.sendCommand(self.factory.method,
            urlparse.urlunparse((None,
                None,
                self.factory.path,
                None,
                self.factory.query,
                None)))
        self.factory.log(self.factory.host)
        self.factory.log(self.factory.agent)
        self.factory.log(self.factory.oauth_header)
        self.sendHeader('Host', self.factory.host)
        self.sendHeader('User-Agent', self.factory.agent)
        self.sendHeader('Authorization', self.factory.oauth_header)
        self.endHeaders()
        self.factory.connectionMade()
        self.transport.setTcpKeepAlive(True)
  
    def handleStatus(self, version, status, message):
        if status != '200':
            self.factory.badStatus(version, status, message)
  
    def lineReceived(self, line):
        self.factory.lineReceived(line)

class CtxFactory(ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ClientContextFactory.getContext(self)
        return ctx

class TwitterStreamerFactory(ReconnectingClientFactory):
    protocol = TwitterStreamer

    def __init__(self, listener, method, path, query, oauth_header):
        self.listener = listener
        self.method = method
        self.path = path
        self.query = query
        self.agent='Twisted/TwitterStreamer'
        self.host = TWITTER_STREAM_API_HOST
        self.oauth_header = oauth_header
    
    def buildProtocol(self, addr):
        self.resetDelay()
        proto = ReconnectingClientFactory.buildProtocol\
                    (self, addr)
        return proto

    def lineReceived(self, line):
        if not self.listener.lineReceived(line):
            self.stopTrying()
            self.stopFactory()

    def badStatus(self, version, status, message):
        self.initialDelay = 10
        self.maxDelay = 240
        self.factory = 2
        self.listener.log('HTTP ERROR: %s: %s: %s' % (str(version),\
                    str(status), str(message)))

    def connectionMade(self):
        self.listener.connectionMade()

    def clientConnectionLost(self, connector, unused_reason):
        self.listener.connectionLost('clientConnectionLost: %s' %
            (str(unused_reason)))
        if self.maxDelay != 240:
            self.initialDelay = 1
            self.maxDelay = 16
            self.factor = 2
        ReconnectingClientFactory.clientConnectionLost(self,
            connector, unused_reason)

    def clientConnectionFailed(self, connector, reason):
        self.listener.connectionLost('clientConnectionFailed %s' %
            (str(reason)))
        ReconnectingClientFactory.clientConnectionFailed(self,
            connector, reason)

    def log(self, message):
        self.listener.log(message)
    
class Stream(object):
    def __init__(self, auth, listener):
        self.auth = auth
        self.listener = listener
        self.scheme = 'https'
        self.host = TWITTER_STREAM_API_HOST
        self.path = ''
        self.query = ''
        self.method = 'GET'
        self.parameters = {}
    
    def _start(self):
        url = urlparse.urlunparse((self.scheme,
            self.host, 
            self.path,
            None,
            self.query,
            None))
        auth_header = self.auth.build_authorization_header(url,
                        self.method,
                        self.parameters)
        twsf = TwitterStreamerFactory(self.listener,
                self.method,
                self.path,
                self.query,
                auth_header)
        from twisted.internet import reactor
        reactor.connectSSL(self.host, 443, twsf, CtxFactory())
        reactor.run()

    def sample(self, **options):
        STREAM_VERSION = 1
        self.command = 'GET'
        self.path = '/%i/statuses/sample.json' % (STREAM_VERSION)
        if isinstance(options, dict):
            for arg, value in options.iteritems():
                if self.query:
                    self.query += '&%s=%s' % (arg, value)
                else:
                    self.query += '%s=%s' % (arg, value)
                self.parameters[arg] = value
        self._start()
