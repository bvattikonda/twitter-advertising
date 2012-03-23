from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import Protocol
import logging
import os
import re
import time

PORT = 9000

class JobDistributor(Protocol):
    def dataReceived(self, data):
        path, pattern = data.split('\t')
        if (path, pattern) not in self.factory.job_listings:
            self.factory.job_listings[(path, pattern)] = list()
            self.factory.finished_jobs[(path, pattern)] = list()

        if not self.factory.job_listings:
            filenames = os.listdir(path)
            for filename in filenames:
                if re.match(pattern, filename) and filename not in\
                    self.factory.finished_jobs:
                    self.factory.job_listings[(path,\
                            pattern)].append(filename)

        if len(self.factory.job_listings) == 0:
            self.transport.write('')
        else:
            job = self.factory.job_listings[0]
            self.transport.write(job)
            self.factory.finished_jobs.append(job)
            del self.factory.job_listings[0]
        self.transport.loseConnection()

class JobDistributionFactory(ServerFactory):
    protocol = JobDistributor

    def __init__(self):
        self.job_listings = dict()
        self.finished_jobs = dict()

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
