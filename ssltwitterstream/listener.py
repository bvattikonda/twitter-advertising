from ssltwitterstream.parser import JSONParser
from ssltwitterstream.streaming import TwitterStreamerFactory

class TwitterStreamListener(TwitterStreamerFactory):
    def __init__(self):
        self.parser = JSONParser()

    def lineReceived(self, line):
        ''' Called when any line arrives 

        Override this method if you wish to manually handle all the
        stream data. Return False to close the connection. Return True
        to keep the connection going.
        '''
        try:
            jsonMessage = self.parser.parse('GET', line)
        except Exception, e:
            if 'HTTP' in line or 'Content-Type:' in line or\
                'Connection' in line or len(line.strip()) == 0:
                return True
            else:
                raise

        ''' ignore delimiter message '''
        if isinstance(jsonMessage, int):
            return True

        if jsonMessage.has_key('text'):
            self.tweetReceived(jsonMessage)
        elif jsonMessage.has_key('delete'):
            status_id = jsonMessage['delete']['status']['id']
            user_id = jsonMessage['delete']['status']['user_id']
            self.deleteTweet(status_id, user_id)
        elif jsonMessage.has_key('warning'):
            code = jsonMessage['warning']['code']
            message = jsonMessage['warning']['message']
            percent_full = jsonMessage['warning']['percent_full']
            self.twitterWarning(code, message, percent_full)
        elif jsonMessage.has_key('scrub_geo'):
            user_id = jsonMessage['scrub_geo']['user_id']
            up_to_status_id =\
                jsonMessage['scrub_geo']['up_to_status_id']
            self.scrubGeo(up_to_status_id, user_id)
        return True

    def tweetReceived(self, tweet):
        ''' Called when a new tweet arrives '''
        return
    
    def deleteTweet(self, status_id, user_id):
        ''' Called when a delete notice arrives for a status '''
        return
    
    def scrubGeo(self, up_to_status_id, user_id):
        ''' Called when a location deletion message arrives '''
        return 

    def twitterWarning(self, code, message, percent_full):
        ''' Called when Twitter sends a warning '''
        return
    
    def connectionMade(self):
        ''' Called when connection is made with Twitter '''
        return

    def connectionLost(self):
        ''' Called when connection with Twitter is lost '''
        return
