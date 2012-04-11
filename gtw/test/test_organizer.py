import unittest
from .organizer_jukebox import OrganizerJukeBox
from ..webinar import Webinar
from ..organizer import GetPastWebinars, GetFutureWebinars, GetSessionedWebinars
from sanetime import time
from ..session import Session
from giftwrap import mocker


class OrganizerTest(unittest.TestCase):
    past_json = u"""
            [   { "webinarKey": 8471, "subject": "Subject1\u2603", "description": "Description1\u2603", "timeZone": "America/New_York", "times": [
                    { "startTime": "2011-06-01T10:00:00Z", "endTime": "2011-06-01T11:00:00Z" } ] },
                { "webinarKey": 2394, "name": "Subject2\u2603", "description": "Description2\u2603", "timeZone": "America/New_York", "times": [
                    { "startTime": "2011-07-01T12:00:00Z", "endTime": "2011-07-01T13:00:00Z" },
                    { "startTime": "2011-07-02T12:00:00Z", "endTime": "2011-07-02T13:00:00Z" } ] } ] """
    future_json = u"""
            [   { "webinarKey": 1034, "subject": "Subject1\u2603", "description": "Description1\u2603", "timeZone": "America/New_York", "times": [
                    { "startTime": "2012-06-01T10:00:00Z", "endTime": "2012-06-01T11:00:00Z" } ] },
            { "webinarKey": 9582, "name": "Subject2\u2603", "description": "Description2\u2603", "timeZone": "America/New_York", "times": [
                    { "startTime": "2012-07-01T12:00:00Z", "endTime": "2012-07-01T13:00:00Z" },
                    { "startTime": "2012-07-02T12:00:00Z", "endTime": "2012-07-02T13:00:00Z" } ] } ] """
    sessioned_json = u"""
            [   { "sessionKey": 4942, "webinarKey": 8471, "startTime": "2011-06-01T10:01:00Z", "endTime": "2011-06-01T11:01:00Z", "registrantsAttended": 11 },
                { "sessionKey": 6043, "webinarKey": 2394, "startTime": "2011-07-01T12:02:00Z", "endTime": "2011-07-01T13:02:00Z", "registrantsAttended": 22 },
                { "sessionKey": 5028, "webinarKey": 2394, "startTime": "2011-07-02T12:02:00Z", "endTime": "2011-07-02T13:02:00Z", "registrantsAttended": 33 },
                { "sessionKey": 4023, "webinarKey": 2394, "startTime": "2011-08-01T12:03:00Z", "endTime": "2011-08-01T13:03:00Z", "registrantsAttended": 44 } ] """

    def setUp(self): self.organizer = OrganizerJukeBox().organizer
    def tearDown(self): pass

    def test_past_webinars(self):
        wa = Webinar(self.organizer, key=8471, subject=u"Subject1\u2603", description=u"Description1\u2603", timezone=u"America/New_York", sessions=[])
        wa.sessions.append(Session(wa, starts_at=time('6/1/11 10:00'), ends_at=time('6/1/11 11:00')))
        wb = Webinar(self.organizer, key=2394, subject=u"Subject2\u2603", description=u"Description2\u2603", timezone=u"America/New_York", sessions=[])
        wb.sessions.append(Session(wb, starts_at=time('7/1/11 12:00'), ends_at=time('7/1/11 13:00')))
        wb.sessions.append(Session(wb, starts_at=time('7/2/11 12:00'), ends_at=time('7/2/11 13:00')))
        with mocker(GetPastWebinars, text=self.past_json):
            self.assertEquals([wa,wb], self.organizer.past_webinars)

    def test_future_webinars(self):
        wa = Webinar(self.organizer, key=1034, subject=u"Subject1\u2603", description=u"Description1\u2603", timezone=u"America/New_York", sessions=[])
        wa.sessions.append(Session(wa, starts_at=time('6/1/12 10:00'), ends_at=time('6/1/12 11:00')))
        wb = Webinar(self.organizer, key=9582, subject=u"Subject2\u2603", description=u"Description2\u2603", timezone=u"America/New_York", sessions=[])
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
        with mocker(GetSessionedWebinars, text=self.sessioned_json):
            self.assertEquals(wa, self.organizer.sessioned_webinars[0])
            self.assertEquals(wb, self.organizer.sessioned_webinars[1])
            self.assertEquals([wa,wb], self.organizer.sessioned_webinars)

    def test_webinars(self):
        wa = Webinar(self.organizer, key=8471, subject=u"Subject1\u2603", description=u"Description1\u2603", timezone=u"America/New_York", sessions=[])
        wa.sessions.append(Session(wa, key=4942, attendant_count=11, started_at=time('6/1/11 10:01'), ended_at=time('6/1/11 11:01'), starts_at=time('6/1/11 10:00'), ends_at=time('6/1/11 11:00')))
        wb = Webinar(self.organizer, key=2394, subject=u"Subject2\u2603", description=u"Description2\u2603", timezone=u"America/New_York", sessions=[])
        wb.sessions.append(Session(wb, key=6043, attendant_count=22, started_at=time('7/1/11 12:02'), ended_at=time('7/1/11 13:02'), starts_at=time('7/1/11 12:00'), ends_at=time('7/1/11 13:00')))
        wb.sessions.append(Session(wb, key=5028, attendant_count=33, started_at=time('7/2/11 12:02'), ended_at=time('7/2/11 13:02'), starts_at=time('7/2/11 12:00'), ends_at=time('7/2/11 13:00')))
        wb.sessions.append(Session(wb, key=4023, attendant_count=44, started_at=time('8/1/11 12:03'), ended_at=time('8/1/11 13:03')))
        wc = Webinar(self.organizer, key=1034, subject=u"Subject1\u2603", description=u"Description1\u2603", timezone=u"America/New_York", sessions=[])
        wc.sessions.append(Session(wc, starts_at=time('6/1/12 10:00'), ends_at=time('6/1/12 11:00')))
        wd = Webinar(self.organizer, key=9582, subject=u"Subject2\u2603", description=u"Description2\u2603", timezone=u"America/New_York", sessions=[])
        wd.sessions.append(Session(wd, starts_at=time('7/1/12 12:00'), ends_at=time('7/1/12 13:00')))
        wd.sessions.append(Session(wd, starts_at=time('7/2/12 12:00'), ends_at=time('7/2/12 13:00')))
        with mocker(GetPastWebinars, text=self.past_json):
            with mocker(GetFutureWebinars, text=self.future_json):
                with mocker(GetSessionedWebinars, text=self.sessioned_json):
                    self.assertEquals([wa,wb,wc,wd], self.organizer.webinars)
                    for w in self.organizer.webinars:
                        for s in w.sessions:
                            self.assertEquals(id(w),id(s.webinar))


    def test_live_listing(self):
        organizer = OrganizerJukeBox()['maggie-prod']
        for w in organizer.webinars:
            if w.key == 519095185:
                for s in w.sessions:
                    lst = {}
                    for r in s.registrants:
                        lst.setdefault(r.email.lower(),[]).append(r)
                    for v in lst.values():
                        if len(v)>1:
                            print v

                #for s in w.sessions:
                    #s.registrants
                #print w
        #print len(organizer.webinars)
        #print sum(len(w.sessions) for w in organizer.webinars)

    @unittest.skip
    def test_maggie(self):
        def f(total, r):
            total.setdefault(r.email,[]).append(r)
            return total
        organizer = OrganizerJukeBox()['maggie']
        for w in organizer.webinars:
            breakdown = reduce(f, w.registrants, {})
            for v in breakdown.values():
                if len(v) > 1: print v

            print len(breakdown)

