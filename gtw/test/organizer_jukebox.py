import os
import json
from utils.property import cached_property
from utils.exception import Error
from ..organizer import Organizer

TEST_ACCOUNTS_FILENAME = 'organizers.json'
COMMON_DISCLAIMER = """
Unittests rely on the existence of the file: '%s', and on it having valid credentials at least for the 'default' key.  See %s.example for what this file should look like.  
These tests also rely on having some scheduled events in the future that have a subject line starting with "Unittest"
""" % (TEST_ACCOUNTS_FILENAME,TEST_ACCOUNTS_FILENAME)

class TestError(Error): pass

class OrganizerJukeBox(object):

    def __getitem__(self, key):
        try:
            return Organizer(**self._organizer_dict[key])
        except KeyError as err:
            msg = "%s doesn't appear to have a 'default' key.  Unittests rely on the creds specified under that key.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)
            TestError(msg, err)._raise()

    @cached_property
    def organizer(self):
        return self.__getitem__('default')

    @cached_property
    def _organizer_dict(self):
        try:
            raw_text = open(os.path.join(os.path.dirname(__file__), TEST_ACCOUNTS_FILENAME)).read()
        except IOError as err:
            msg = "Unable to open '%s' for integration tests.\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)
            TestError(msg, err)._raise()
        try:
            d = json.loads(raw_text)
        except ValueError as err:
            msg = "'%s' doesn't appear to be valid json!\n\n%s" % (TEST_ACCOUNTS_FILENAME, COMMON_DISCLAIMER)
            TestError(msg, err)._raise()
        return d


