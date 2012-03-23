from twisted.internet.protocol import ServerFactory
from twisted.internet.protocol import Protocol
import logging
import os
import re
import time

PORT = 9000

class JobDistributor(Protocol):
    def connectionMade(self):
        print 'New connection received'

    def dataReceived(self, data):
        task_id, path, pattern = data.split('\t')
        job_key = (task_id, path, pattern)
        if job_key not in self.factory.job_listings:
            self.factory.job_listings[job_key] = list()
            self.factory.finished_jobs[job_key] = list()

        if not self.factory.job_listings[job_key]:
            filenames = os.listdir(path)
            print len(filenames)
            for filename in filenames:
                if re.match(pattern, filename) and filename not in\
                    self.factory.finished_jobs[job_key]:
                    self.factory.job_listings[job_key].append(filename)

        if len(self.factory.job_listings[job_key]) == 0:
            print 'Sending no job'
            self.transport.write('')
        else:
            job = self.factory.job_listings[job_key][0]
            print 'Sending %s' % (job)
            self.transport.write(job)
            self.factory.finished_jobs[job_key].append(job)
            del self.factory.job_listings[job_key][0]
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
