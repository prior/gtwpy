from giftwrap import Auth as BaseAuth

class Auth(BaseAuth):
    domain = 'api.citrixonline.com'

    def __init__(self, oauth_token, organizer_key):
        super(BaseAuth, self).__init__()
        self.oauth_token
        self.organizer_key

    def _base_path(self):
        return 'G2W/rest/organizers/%s' % self.organized_key

    def _headers(self):
        return {'Authorization': 'OAuth oauth_token=%s'%self.oauth_token}

