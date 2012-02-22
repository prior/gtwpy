import os
import json
from gtw.error import GTWError


def get_creds(key='default'):
    filename = 'test_credentials.json'
    try:
        raw_text = open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError:
        raise GTWError, """Unable to open '%s' for integration tests.\n
  These tests rely on the existence of that file and on it having valid webex credentials.""" % filename
    try:
        creds = json.loads(raw_text)[key]
    except ValueError:
        raise GTWError, """'%s' doesn't appar to be valid json!\n
  These tests rely on the existence of that file and on it having valid webex credentials.""" % filename
    return creds


