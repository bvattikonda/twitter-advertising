from ssltwitterstream.utils import import_json
from ssltwitterstream.error import SSLTwitterError

class Parser(object):
    def parse(self, method, payload):
        """
        Parse the response payload and return the result.
        Returns a tuple that contains the result data
        """
        raise NotImplementedError

    def parse_error(self, payload):
        """
        Parse the error message from payload.
        If unable to parse the message, throw an exception
        and default error message will be used.
        """
        raise NotImplementedError

   
class JSONParser(Parser):
    
    def __init__(self):
        self.json_lib = import_json()

    def parse(self, method, payload):
        try:
            json = self.json_lib.loads(payload)
        except Exception, e:
            SSLTwitterError('Failed to parse payload: %s' % e)
            raise
        return json
    
    def parse_error(self, payload):
        error = self.json_lib.loads(payload)
        if error.has_key('error'):
            return error['error']
        else:
            return error['errors']
