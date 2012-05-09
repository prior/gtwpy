import unittest
from .organizer_jukebox import OrganizerJukeBox
from ..webinar import Webinar, GetRegistrations
from ..session import Session, GetAttendees
from ..registrant import Registrant
from sanetime import time
from giftwrap import mocker


class SessionTest(unittest.TestCase):
    registrants_json = u"""
            [   { "registrantKey": 9583, "firstName":"J\u00f6hn", "lastName":"Smith", "status":"APPROVED", "email":"jsmith@test.com", "registrationDate":"2012-05-01T18:01:00Z", "joinUrl":"http://bit.ly/482024" },
                { "registrantKey": 2305, "firstName":"Suzy", "lastName":"Samwell", "status":"APPROVED", "email":"ss@test.com", "registrationDate":"2012-05-02T18:02:00Z", "joinUrl":"http://bit.ly/8592932" },
                { "registrantKey": 4203, "firstName":"Todd", "lastName":"Kells", "status":"WAITING", "email":"tkells@test.com", "registrationDate":"2012-05-03T18:03:00Z", "joinUrl":"http://bit.ly/9293842" } ] """

    attendees_json = u"""
            [   { "registrantKey":9583, "firstName":"J\u00f6hn", "lastName":"Smith", "email":"jsmith@test.com", "attendanceTimeInSeconds":3293, "attendance": [{"joinTime": "2011-04-01T12:01:00Z", "leaveTime": "2011-04-01T12:22:00Z"}] },
                { "registrantKey":2305, "firstName":"Suzy", "lastName":"Samwell", "email":"ss@test.com", "attendanceTimeInSeconds":4931, "attendance": [{"joinTime": "2011-04-01T12:02:00Z", "leaveTime": "2011-04-01T12:07:00Z"}, {"joinTime": "2011-04-01T12:12:00Z", "leaveTime": "2011-04-01T12:17:00Z"}, {"joinTime": "2011-04-01T12:22:00Z", "leaveTime": "2011-04-01T12:27:00Z"}] } ] """
                

    def setUp(self): self.organizer = OrganizerJukeBox().organizer
    def tearDown(self): pass

    def test_attendees(self):
        w = Webinar(self.organizer, key=2394, timezone='America/New_York', sessions=[])
        s = Session(w, key=6043, started_at=time('2012-06-01'), attendees=[])
        a1 = Registrant(webinar=w, session=s, key=9583, first_name=u'J\u00f6hn', last_name=u'Smith', email=u'jsmith@test.com', viewings=[(time('4/1/11 12:01'), time('4/1/11 12:22'))])
        a2 = Registrant(webinar=w, session=s, key=2305, first_name=u'Suzy', last_name=u'Samwell', email=u'ss@test.com', viewings=[(time('4/1/11 12:02'), time('4/1/11 12:07')),(time('4/1/11 12:12'), time('4/1/11 12:17')),(time('4/1/11 12:22'), time('4/1/11 12:27'))])
        with mocker(GetAttendees, text=self.attendees_json):
            session = Session(w, key=6043, started_at=time('2012-06-01'))
            self.assertEquals([a1,a2], session.attendees)

    def test_registrants(self):
        w = Webinar(self.organizer, key=2394, timezone='America/New_York', sessions=[])
        s = Session(w, key=6043, started_at=time('2012-06-01'), attendees=[])
        r1 = Registrant(webinar=w, session=s, key=9583, first_name=u'J\u00f6hn', last_name=u'Smith', email=u'jsmith@test.com', registered_at='5/1/12 18:01', join_url='http://bit.ly/482024', status='APPROVED', viewings=[(time('4/1/11 12:01'), time('4/1/11 12:22'))])
        r2 = Registrant(webinar=w, session=s, key=2305, first_name=u'Suzy', last_name=u'Samwell', email=u'ss@test.com', registered_at='5/2/12 18:02', join_url='http://bit.ly/8592932', status='APPROVED', viewings=[(time('4/1/11 12:02'), time('4/1/11 12:07')),(time('4/1/11 12:12'), time('4/1/11 12:17')),(time('4/1/11 12:22'), time('4/1/11 12:27'))])
        r3 = Registrant(webinar=w, session=s, key=4203, first_name=u'Todd', last_name=u'Kells', email=u'tkells@test.com', registered_at='5/3/12 18:03', join_url='http://bit.ly/9293842', status='WAITING', viewings=[])
        with mocker(GetAttendees, text=self.attendees_json):
            with mocker(GetRegistrations, text=self.registrants_json):
                session = Session(w, key=6043, started_at=time('2012-06-01'))
                self.assertEquals([r1,r2,r3], session.registrants)

    def test_universal_key(self):
        w = Webinar(self.organizer, key=4918, timezone='America/New_York', sessions=[])
        sa = Session(w, key=2058, started_at=time('2012-06-01'))
        sb = Session(w, key=2023, started_at=time('2012-06-02'))
        sc = Session(w, key=2084, started_at=time('2012-06-03'))
        w.sessions.append(sa)
        w.sessions.append(sb)
        w.sessions.append(sc)
        self.assertEquals('4918-1', sa.universal_key)
        self.assertEquals('4918-2', sb.universal_key)
        self.assertEquals('4918-3', sc.universal_key)


