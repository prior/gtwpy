from sanetime import ntime
from utils.property import cached_property, cached_value, cached_key, is_cached
from utils.dict import mget
from utils.list import sort
from utils.obj import kwargs_str
from . import mixins
from giftwrap import JsonExchange
from .registrant import Registrant
from .base import Base


class Session(Base, mixins.Session):
    def __init__(self, webinar, **kwargs):
        super(Session, self).__init__()
        self.webinar = webinar
        self.key = mget(kwargs,'sessionKey','key')
        self.attendant_count = mget(kwargs, 'attendant_count', 'registrantsAttended')
        if kwargs.has_key('attendees'): self.attendees = kwargs['attendees']

        actual = kwargs.get('actual')
        scheduled = kwargs.get('scheduled')
        self._starts_at = ntime(mget(kwargs,'starts_at','_starts_at') or scheduled and kwargs.get('startTime'))
        self._ends_at = ntime(mget(kwargs,'ends_at','_ends_at') or scheduled and kwargs.get('endTime'))
        self._started_at = ntime(mget(kwargs,'started_at','_started_at') or actual and kwargs.get('startTime'))
        self._ended_at = ntime(mget(kwargs,'ended_at','_ended_at') or actual and kwargs.get('endTime'))

    def __repr__(self): 
        return "Session(%s)" % kwargs_str(self,attrs=['key','_starts_at','_ends_at','_started_at','_ended_at','attendant_count'], cached=['attendees'])
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        webinar_key = self.webinar and self.webinar.key or '?'
        subject = self.webinar and self.webinar.subject or '?'
        session_key = self.key or '?'
        starts_at = self._starts_at and "%s +%s" % (self.tz_starts_at.strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        ends_at = self._ends_at and "%s +%s" % (self.tz_ends_at.strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        started_at = self._started_at and "%s +%s" % (self.tz_started_at.strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        ended_at = self._ended_at and "%s +%s" % (self.tz_ended_at.strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        count = self.attendant_count is None and '?' or self.attendant_count
        registrants = "\n  ".join(['']+[unicode(s) for s in cached_value(self,'registrants',[])])
        return u"S[%s] W[%s:%s] s:(%s - %s) h:(%s - %s) +%s  ^%s%s" % (session_key, webinar_key, subject, starts_at, ends_at, started_at, ended_at, self.timezone, count, registrants)

    def duration(self):
        return self.started_at and self.ended_at and self.started_at - self.ended_at

    @cached_property
    def _attendees_ex(self): return GetAttendees(self)

    @cached_property
    def attendees(self): return self.key and self._attendees_ex.result

    @cached_property
    def registrants(self):
        if not self.key: return self.webinar.registrants
        SessionExchange.async_exchange([self.webinar._registrations_ex, self._attendees_ex])
        _registrants = [r.clone() for r in self.webinar.registrants]
        attendee_dict = dict((a.email,a) for a in self.attendees)
        for r in _registrants:
            r.session = self
            if attendee_dict.get(r.email): r.merge(attendee_dict[r.email])
        return _registrants

    def merge(self, session):
        self._merge_primitives(session, 'key','attendant_count','_starts_at','_ends_at','_started_at','_ended_at')
        self._merge_cached_exchange_collection(session, 'attendees', keys=['email'])
        return self

    def __cmp__(self, other): return self._cmp_components(other, 'starts_at','ends_at','started_at','ended_at','key','attendant_count', cached_key('attendees'))

    @property  #ghetto webinar/session key -- useful for future events that don't have a session key yet
    def universal_key(self):
        if not self.webinar or not self.webinar.key or not is_cached(self.webinar,'sessions') or self not in self.webinar.sessions: return None
        return "%s-%s" % (self.webinar.key, self.webinar.sessions.index(self)+1)


class SessionExchange(JsonExchange):
    def __init__(self, session, **kwargs):
        super(SessionExchange, self).__init__(session.webinar.organizer, **kwargs)
        self.session = session

class GetAttendees(SessionExchange):
        def sub_path(self): return 'webinars/%s/sessions/%s/attendees'%(self.session.webinar.key,self.session.key)
        def process_data(self, data, response): 
            return sort([Registrant(session=self.session,webinar=self.session.webinar,**kwargs) for kwargs in data])

