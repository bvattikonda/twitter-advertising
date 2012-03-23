from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import Protocol
import logging
import time

PORT = 9000
class JobDistributor(Protocol):
    def dataReceived(self, data):
        splitdata = data.split('\t')
        print splitdata
        self.transport.write('This is the new data')
        self.transport.loseConnection()

class JobDistributionFactory(ServerFactory):
    protocol = JobDistributor

def main():
    logging.basicConfig(filename = 'job_distributor.log',
        format = '%(asctime)s - %(levelname)s - %(message)s',\
        level = logging.DEBUG)
    logging.critical('Start server')
    factory = JobDistributionFactory()
    from twisted.internet import reactor
    reactor.listenTCP(PORT, factory)
    reactor.run()

if __name__ == '__main__':
    main()
