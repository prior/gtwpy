class GTWError(ValueError): pass
class GTWApiError(GTWError):
    def __init__(self, response_code=None, response_text=None):
        super(GTWApiError,self).__init__()
        self.code = response_code
        self.text = response_text

class Timeout(GTWError): pass
class BadRequest(GTWApiError): pass
class LockedAccount(GTWApiError): pass
class ServiceDown(GTWApiError): pass
class Unknown(GTWApiError): pass

