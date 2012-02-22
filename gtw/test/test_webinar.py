import unittest2
from ..webinar import Webinar
from pprint import pprint

class WebinarTest(unittest2.TestCase):

    # these integration tests are normally commented out so we don't incur their hits on every run of our test suite
    def setUp(self):
        pass
        #print "\r"
        #self.account = helper.get_account()
        #self.event_controller = EventController(self.account)

    def test_historical_listing(self):
        pprint(Webinar.historical())

    def test_upcoming_listing(self):
        pprint(Webinar.upcoming())

    def test_all(self):
        pprint(Webinar.all())

    def test_webinar_details(self):
        pprint(Webinar.get('189763895'))
        pprint(Webinar.get('881725327'))
        pprint(Webinar.get('141360359'))

        #new_events = [helper.generate_event(), helper.generate_event()]
        #session_keys = [ev.session_key for ev in self.event_controller.list_()]
        #self.assertEquals(len(session_keys), self.event_controller.count)
        #for ev in new_events:
            #self.assertNotIn(ev.session_key, session_keys)
            #self.event_controller.create(ev)
        #session_keys = [ev.session_key for ev in self.event_controller.list_()]
        #self.assertEquals(len(session_keys), self.event_controller.count)
        #for ev in new_events:
            #self.assertIn(ev.session_key, session_keys)
            #self.event_controller.delete(ev)

