import unittest
from .organizer_jukebox import OrganizerJukeBox
from ..webinar import Webinar
from ..organizer import GetPastWebinars, GetFutureWebinars, GetSessionedWebinars
from sanetime import time
from ..session import Session
from giftwrap import mocker
#from ..organizer import Organizer
from ..registrant import Registrant

TEST_UNICODE = False  # have to factor this out so its easily un/commentable, cuz nosetests can't deal with unicode apparently-- awesome
UNICODE_STEM = u'\u2603' if TEST_UNICODE else '^'

def subject(identifier): return u'Test Subject #%s %s' % (identifier,UNICODE_STEM)
def description(identifier): return u'Test Description #%s %s' % (identifier,UNICODE_STEM)


class OrganizerTest(unittest.TestCase):
    past_json = u"""
            [   { "webinarKey": 8471, "subject": "%s", "description": "%s", "timeZone": "America/New_York", "times": [
                    { "startTime": "2011-06-01T10:00:00Z", "endTime": "2011-06-01T11:00:00Z" } ] },
                { "webinarKey": 2394, "name": "%s", "description": "%s", "timeZone": "America/New_York", "times": [
                    { "startTime": "2011-07-01T12:00:00Z", "endTime": "2011-07-01T13:00:00Z" },
                    { "startTime": "2011-07-02T12:00:00Z", "endTime": "2011-07-02T13:00:00Z" } ] }, 
                { "webinarKey": 3948, "subject": "%s", "description": "%s", "timeZone": "America/Los_Angeles", "times": [
                    { "startTime": "2011-09-01T13:00:00Z", "endTime": "2011-09-01T14:00:00Z" } ] } ] """ % tuple([y for x in [[subject(i),description(i)] for i in [1,2,3]] for y in x])
    future_json = u"""
            [   { "webinarKey": 1034, "subject": "%s", "description": "%s", "timeZone": "America/New_York", "times": [
                    { "startTime": "2012-06-01T10:00:00Z", "endTime": "2012-06-01T11:00:00Z" } ] },
            { "webinarKey": 9582, "name": "%s", "description": "%s", "timeZone": "America/New_York", "times": [
                    { "startTime": "2012-07-01T12:00:00Z", "endTime": "2012-07-01T13:00:00Z" },
                    { "startTime": "2012-07-02T12:00:00Z", "endTime": "2012-07-02T13:00:00Z" } ] } ] """ % tuple([y for x in [[subject(i),description(i)] for i in [8,9]] for y in x])
    sessioned_json = u"""
            [   { "sessionKey": 4942, "webinarKey": 8471, "startTime": "2011-06-01T10:01:00Z", "endTime": "2011-06-01T11:01:00Z", "registrantsAttended": 11 },
                { "sessionKey": 6043, "webinarKey": 2394, "startTime": "2011-07-01T12:02:00Z", "endTime": "2011-07-01T13:02:00Z", "registrantsAttended": 22 },
                { "sessionKey": 5028, "webinarKey": 2394, "startTime": "2011-07-02T12:02:00Z", "endTime": "2011-07-02T13:02:00Z", "registrantsAttended": 33 },
                { "sessionKey": 4023, "webinarKey": 2394, "startTime": "2011-08-01T12:03:00Z", "endTime": "2011-08-01T13:03:00Z", "registrantsAttended": 44 },
                { "sessionKey": 8427, "webinarKey": 3948, "startTime": "2011-09-01T18:04:00Z", "endTime": "2011-09-01T19:04:00Z", "registrantsAttended": 55 } ] """

    def setUp(self): self.organizer = OrganizerJukeBox().organizer
    def tearDown(self): pass

    def test_past_webinars(self):
        wa = Webinar(self.organizer, key=8471, subject=subject(1), description=description(1), timezone=u"America/New_York", sessions=[])
        wa.sessions.append(Session(wa, starts_at=time('6/1/11 10:00'), ends_at=time('6/1/11 11:00')))
        wb = Webinar(self.organizer, key=2394, subject=subject(2), description=description(2), timezone=u"America/New_York", sessions=[])
        wb.sessions.append(Session(wb, starts_at=time('7/1/11 12:00'), ends_at=time('7/1/11 13:00')))
        wb.sessions.append(Session(wb, starts_at=time('7/2/11 12:00'), ends_at=time('7/2/11 13:00')))
        wc = Webinar(self.organizer, key=3948, subject=subject(3), description=description(3), timezone=u"America/Los_Angeles", sessions=[])
        wc.sessions.append(Session(wc, starts_at=time('9/1/11 13:00'), ends_at=time('9/1/11 14:00')))
        with mocker(GetPastWebinars, text=self.past_json):
            self.assertEquals([wa,wb,wc], self.organizer.past_webinars)

    def test_future_webinars(self):
        wa = Webinar(self.organizer, key=1034, subject=subject(8), description=description(8), timezone=u"America/New_York", sessions=[])
        wa.sessions.append(Session(wa, starts_at=time('6/1/12 10:00'), ends_at=time('6/1/12 11:00')))
        wb = Webinar(self.organizer, key=9582, subject=subject(9), description=description(9), timezone=u"America/New_York", sessions=[])
        wb.sessions.append(Session(wb, starts_at=time('7/1/12 12:00'), ends_at=time('7/1/12 13:00')))
        wb.sessions.append(Session(wb, starts_at=time('7/2/12 12:00'), ends_at=time('7/2/12 13:00')))
        with mocker(GetFutureWebinars, text=self.future_json):
            self.assertEquals([wa,wb], self.organizer.future_webinars)

    def test_sessioned_webinars(self):
        wa = Webinar(self.organizer, key=8471, sessions=[])
        wa.sessions.append(Session(wa, key=4942, attendant_count=11, started_at=time('6/1/11 10:01'), ended_at=time('6/1/11 11:01')))
        wb = Webinar(self.organizer, key=2394, sessions=[])
        wb.sessions.append(Session(wb, key=6043, attendant_count=22, started_at=time('7/1/11 12:02'), ended_at=time('7/1/11 13:02')))
        wb.sessions.append(Session(wb, key=5028, attendant_count=33, started_at=time('7/2/11 12:02'), ended_at=time('7/2/11 13:02')))
        wb.sessions.append(Session(wb, key=4023, attendant_count=44, started_at=time('8/1/11 12:03'), ended_at=time('8/1/11 13:03')))
        wc = Webinar(self.organizer, key=3948, sessions=[])
        wc.sessions.append(Session(wc, key=8427, attendant_count=55, started_at=time('9/1/11 18:04'), ended_at=time('9/1/11 19:04')))
        with mocker(GetSessionedWebinars, text=self.sessioned_json):
            self.assertEquals(wa, self.organizer.sessioned_webinars[0])
            self.assertEquals(wb, self.organizer.sessioned_webinars[1])
            self.assertEquals(wc, self.organizer.sessioned_webinars[2])
            self.assertEquals([wa,wb,wc], self.organizer.sessioned_webinars)

    def test_webinars(self):
        wa = Webinar(self.organizer, key=8471, subject=subject(1), description=description(1), timezone=u"America/New_York", sessions=[])
        wa.sessions.append(Session(wa, key=4942, attendant_count=11, started_at=time('6/1/11 10:01'), ended_at=time('6/1/11 11:01'), starts_at=time('6/1/11 10:00'), ends_at=time('6/1/11 11:00')))
        wb = Webinar(self.organizer, key=2394, subject=subject(2), description=description(2), timezone=u"America/New_York", sessions=[])
        wb.sessions.append(Session(wb, key=6043, attendant_count=22, started_at=time('7/1/11 12:02'), ended_at=time('7/1/11 13:02'), starts_at=time('7/1/11 12:00'), ends_at=time('7/1/11 13:00')))
        wb.sessions.append(Session(wb, key=5028, attendant_count=33, started_at=time('7/2/11 12:02'), ended_at=time('7/2/11 13:02'), starts_at=time('7/2/11 12:00'), ends_at=time('7/2/11 13:00')))
        wb.sessions.append(Session(wb, key=4023, attendant_count=44, started_at=time('8/1/11 12:03'), ended_at=time('8/1/11 13:03')))
        wc = Webinar(self.organizer, key=3948, subject=subject(3), description=description(3), timezone=u"America/Los_Angeles", sessions=[])
        wc.sessions.append(Session(wc, key=8427, attendant_count=55, started_at=time('9/1/11 18:04'), ended_at=time('9/1/11 19:04'), starts_at=time('9/1/11 13:00'), ends_at=time('9/1/11 14:00')))
        wd = Webinar(self.organizer, key=1034, subject=subject(8), description=description(8), timezone=u"America/New_York", sessions=[])
        wd.sessions.append(Session(wd, starts_at=time('6/1/12 10:00'), ends_at=time('6/1/12 11:00')))
        we = Webinar(self.organizer, key=9582, subject=subject(9), description=description(9), timezone=u"America/New_York", sessions=[])
        we.sessions.append(Session(we, starts_at=time('7/1/12 12:00'), ends_at=time('7/1/12 13:00')))
        we.sessions.append(Session(we, starts_at=time('7/2/12 12:00'), ends_at=time('7/2/12 13:00')))
        with mocker(GetPastWebinars, text=self.past_json):
            with mocker(GetFutureWebinars, text=self.future_json):
                with mocker(GetSessionedWebinars, text=self.sessioned_json):
                    self.assertEquals([wa,wb,wc,wd,we], self.organizer.webinars)
                    for w in self.organizer.webinars:
                        for s in w.sessions:
                            self.assertEquals(id(w),id(s.webinar))


#    @unittest.skip
    def test_live_listing(self):
        organizer = OrganizerJukeBox()['gmig']
        for w in organizer.webinars:
            for s in w.sessions:
                s.registrants
            print w
        print len(organizer.webinars)
        print sum(len(w.sessions) for w in organizer.webinars)

    @unittest.skip
    def test_registration(self):
        organizer = OrganizerJukeBox()['default']
        for w in organizer.webinars:
            if w.key == 170884119:
                #Registrant.random(w).create()
                Registrant._create(Registrant.random(w,count=10))


    @unittest.skip
    def test_maggie(self):
        org = OrganizerJukeBox()['maggie-qa']
        for w in org.webinars:
            for s in w.sessions:
                if s.universal_key == '622344800-1':
                    s.registrants
                    print s

        #print len(org.webinars)
#        print len(Organizer(key='2710905', oauth='7798e0bf46acca038cfbd2ac3849f77').webinars)

    #@unittest.skip
    #def test_wtf(self):
        #org = OrganizerJukeBox()['maggie-qa']
        #for w in org.webinars:

            #if w.key == 760633440:
                #print len(w.registrants)
                #print len(w.sessions)
                #print w.sessions[0]
                #print len(w.sessions[0].attendees)
                #print w.sessions[1]
                #print len(w.sessions[1].attendees)
                ##print w.sessions[2]
                ##print len(w.sessions[2].attendees)
                ##print w.sessions[3]
                ##print len(w.sessions[3].attendees)
                ##print w.sessions[4]
                ##print len(w.sessions[4].attendees)
                ##print w.sessions[5]
                ##print len(w.sessions[5].attendees)

