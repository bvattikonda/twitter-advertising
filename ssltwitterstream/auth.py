from ssltwitterstream import oauth

class Auth:
    def __init__(self, consumer_key, consumer_secret, access_token,
        access_secret):
        self.consumer = oauth.OAuthConsumer(consumer_key,\
                        consumer_secret)
        self.access_token = oauth.OAuthToken(key = access_token,\
                        secret = access_secret)
    

    def build_authorization_header(self, url, method, parameters):
        request = oauth.OAuthRequest.from_consumer_and_token(
                    self.consumer,
                    http_url = url,
                    http_method = method,
                    token = self.access_token,
                    parameters = parameters) 
        request.sign_request(oauth.OAuthSignatureMethod_HMAC_SHA1(),
            self.consumer,
            self.access_token)
        header = request.to_header()['Authorization'].encode('utf-8')
        return header
