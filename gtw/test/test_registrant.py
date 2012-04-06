import unittest
from .organizer_jukebox import OrganizerJukeBox
from ..webinar import Webinar
from ..session import Session
from ..registrant import Registrant, CreateRegistrant
from sanetime import delta, time
from giftwrap import mocker


class SessionTest(unittest.TestCase):
    registered_json = u""" { "registrantKey":2038, "joinUrl":"https://bit.ly/00293423" } """

    def setUp(self): self.organizer = OrganizerJukeBox().organizer
    def tearDown(self): pass

    def test_register(self):
        w = Webinar(self.organizer, key=2394, timezone='America/New_York', sessions=[])
        s = Session(w, key=6043, started_at=time('2012-06-01'), attendees=[])
        s.attendees.append(Registrant(webinar=w, session=s, key=2305, first_name=u'Suzy', last_name=u'Samwell', email=u'ss@test.com', duration=delta(s=4931)))
        with mocker(CreateRegistrant, text=self.registered_json):
            seed_registrant = Registrant(webinar=w, session=s, first_name=u'J\u00f6hn', last_name=u'Smith', email=u'jsmith@test.com')
            expected_registrant = Registrant(webinar=w, session=s, key=2038, first_name=u'J\u00f6hn', last_name=u'Smith', email=u'jsmith@test.com', join_url='https://bit.ly/00293423')
            self.assertEquals(expected_registrant, seed_registrant.create())


