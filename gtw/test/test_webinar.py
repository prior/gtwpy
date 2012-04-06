import unittest
from .organizer_jukebox import OrganizerJukeBox
from ..webinar import Webinar, GetSessions, GetRegistrants
from ..session import Session
from ..registrant import Registrant
from sanetime import time
from giftwrap import mocker


class WebinarTest(unittest.TestCase):
    sessions_json = u"""
            [   { "sessionKey": 6043, "webinarKey": 2394, "startTime": "2011-07-01T12:02:00Z", "endTime": "2011-07-01T13:02:00Z", "registrantsAttended": 22 },
                { "sessionKey": 5028, "webinarKey": 2394, "startTime": "2011-07-02T12:02:00Z", "endTime": "2011-07-02T13:02:00Z", "registrantsAttended": 33 } ] """
    registrants_json = u"""
            [   { "registrantKey": 9583, "firstName":"J\u00f6hn", "lastName":"Smith", "status":"WAITING", "email":"jsmith@test.com", "registrationDate":"2012-05-01T18:01:00Z", "joinUrl":"http://bit.ly/482024" },
                { "registrantKey": 2305, "firstName":"Suzy", "lastName":"Samwell", "status":"APPROVED", "email":"ss@test.com", "registrationDate":"2012-05-02T18:02:00Z", "joinUrl":"http://bit.ly/8592932" } ] """

    def setUp(self): self.organizer = OrganizerJukeBox().organizer
    def tearDown(self): pass

    def test_sessions(self):
        w = Webinar(self.organizer, key=2394, sessions=[])
        w.sessions.append(Session(w, key=6043, attendant_count=22, started_at=time('7/1/11 12:02'), ended_at=time('7/1/11 13:02')))
        w.sessions.append(Session(w, key=5028, attendant_count=33, started_at=time('7/2/11 12:02'), ended_at=time('7/2/11 13:02')))
        with mocker(GetSessions, text=self.sessions_json):
            self.assertEquals(w.sessions, Webinar(self.organizer, key=2394).sessions)

    def test_registrants(self):
        w = Webinar(self.organizer, key=2394, registrants=[])
        w.registrants.append(Registrant(webinar=w, key=9583, first_name=u'J\u00f6hn', last_name=u'Smith', email=u'jsmith@test.com', registered_at='5/1/12 18:01', join_url='http://bit.ly/482024', status='WAITING'))
        w.registrants.append(Registrant(webinar=w, key=2305, first_name=u'Suzy', last_name=u'Samwell', email=u'ss@test.com', registered_at='5/2/12 18:02', join_url='http://bit.ly/8592932', status='APPROVED'))
        with mocker(GetRegistrants, text=self.registrants_json):
            self.assertEquals(w.registrants, Webinar(self.organizer, key=2394).registrants)


