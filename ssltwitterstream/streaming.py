#!/usr/bin/python
from ssltwitterstream import oauth
from OpenSSL import SSL
import urlparse, time, webbrowser
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.ssl import ClientContextFactory
from twisted.web import http
import time

TWITTER_STREAM_API_HOST = 'stream.twitter.com'

class TwitterStreamer(http.HTTPClient):
    def build_oauth_header(self):
        oauth_header =\
                      self.factory.auth.build_authorization_header(\
                      self.factory.url,\
                      self.factory.method,\
                      self.factory.parameters)
        return oauth_header

    def sendHeaders(self):
        oauth_header = self.build_oauth_header()
        self.factory.log(self.factory.host)
        self.factory.log(self.factory.agent)
        self.factory.log(oauth_header)
        self.sendHeader('Host', self.factory.host)
        self.sendHeader('User-Agent', self.factory.agent)
        self.sendHeader('Authorization', oauth_header)
        self.endHeaders()

    def connectionMade(self):
        self.sendCommand(self.factory.method,
            urlparse.urlunparse((None,
                None,
                self.factory.path,
                None,
                self.factory.query,
                None)))
        self.sendHeaders()
        self.transport.setTcpKeepAlive(True)
        self.factory.connectionMade()
        self.statusLineReceived = False
  
    def handleStatus(self, version, status, message):
        if status != 200:
            self.factor.badStatus(version, status, message)
  
    def lineReceived(self, line):
        if not self.statusLineReceived:
            self.statusLineReceived = True
            version, status, message = line.split(' ', 2)
            self.handleStatus(version, int(status), message)
        self.factory.lineReceived(line)

class CtxFactory(ClientContextFactory):
    def getContext(self):
        self.method = SSL.SSLv23_METHOD
        ctx = ClientContextFactory.getContext(self)
        return ctx

class TwitterStreamerFactory(ReconnectingClientFactory):
    protocol = TwitterStreamer

    def __init__(self, listener, scheme, method, path, query,
        parameters, host, auth):
        self.listener = listener
        self.scheme = scheme
        self.method = method
        self.path = path
        self.query = query
        self.parameters = parameters
        self.host = host
        self.auth = auth 
        self.agent='Twisted/TwitterStreamer'
        self.url = urlparse.urlunparse((self.scheme,
                    self.host,
                    self.path,
                    None,
                    self.query,
                    None))
    
    def buildProtocol(self, addr):
        self.resetDelay()
        self.initialDelay = 1
        self.maxDelay = 16
        self.factor = 2
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
        self.factor = 2
        self.listener.log('HTTP ERROR: %s: %d: %s' % (version,\
                    status, message))

    def connectionMade(self):
        self.listener.connectionMade()

    def clientConnectionLost(self, connector, unused_reason):
        self.listener.connectionLost('clientConnectionLost: %s' %
            (str(unused_reason)))
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
        self.path = ''
        self.query = ''
        self.method = 'GET'
        self.parameters = {}
        self.host = TWITTER_STREAM_API_HOST
    
    def _start(self):
        twsf = TwitterStreamerFactory(self.listener,
                self.scheme,
                self.method,
                self.path,
                self.query,
                self.parameters,
                self.host,
                self.auth)
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
