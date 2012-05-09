from utils.dict import mget
from utils.string import nstrip,nlower
from utils.property import cached_property
from utils.list import sort
from sanetime import ntime, delta, time
from .base import Base
from giftwrap import JsonExchange
from uuid import uuid4


class Registrant(Base):
    def __init__(self, **kwargs):
        super(Registrant, self).__init__()
        self.webinar = kwargs.get('webinar')
        self.session = kwargs.get('session')
        self.key = mget(kwargs, 'key', 'registrant_key', 'registrantKey')
        self.email = nlower(mget(kwargs, 'email', 'attendeeEmail'))
        self.first_name = mget(kwargs, 'first_name', 'firstName', 'first')
        self.last_name = mget(kwargs, 'last_name', 'lastName', 'last')
        if kwargs.get('name'): self.name = nstrip(kwargs.get('name'))
        self.registered_at = ntime(mget(kwargs, 'registered_at', 'registrationDate'))
        self.join_url = mget(kwargs, 'join_url', 'joinUrl')
        self.status = kwargs.get('status')
        self.viewings = kwargs.get('viewings',[])
        if not self.viewings and kwargs.get('attendance'):
            self.viewings = sort([(time(d['joinTime']),time(d['leaveTime'])) for d in kwargs['attendance']])
        if not self.viewings and (kwargs.get('duration') or kwargs.get('attendanceTimeInSeconds')) and self.session and self.session.key and self.session.started_at:
            duration = kwargs.get('duration') or kwargs.get('attendanceTimeInSeconds') and delta(s=kwargs['attendanceTimeInSeconds'])
            self.viewings = [(self.session.started_at, self.session.started_at+duration)]

    @property
    def name(self): return ('%s %s' % (self.first_name or '', self.last_name or '')).strip()
    @name.setter
    def name(self, n):
        parts = n.split(' ')
        self.first_name = self.first_name or ' '.join(parts[0:-1]).strip() or None
        self.last_name = self.last_name or parts[-1].strip() or None

    @property
    def started_at(self): return self.viewings and self.viewings[0][0] or None

    @property
    def ended_at(self): return self.viewings and self.viewings[-1][-1] or None

    @property
    def duration(self): return self.viewings and (self.viewings[-1][-1] - self.viewings[0][0]) or None

    def merge(self, other):
        self._merge_primitives(other, 'webinar', 'session', 'key', 'email', 'first_name', 'last_name', 'registered_at', 'join_url', 'status')
        viewings = []
        for v in sort(self.viewings + other.viewings):
            if viewings:
                last = viewings[-1]
                if v[0]<=last[-1]:
                    viewings[-1] = (min(v[0],last[0]),max(v[-1],last[-1]))
                    continue
            viewings.append(v)
        self.viewings = viewings
        return self

    def __cmp__(self, other): return self._cmp_components(other, 'email', 'last_name', 'first_name', 'started_at', 'ended_at', 'key', 'registered_at', 'join_url', 'status', 'viewings')

    def clone(self): return Registrant().merge(self)

    def create(self): return self._create_ex.result

    @classmethod
    def _create(kls, registrants): return CreateRegistrant.bulk_results([r._create_ex for r in registrants], async=False)  # otherwise we api rate limits

    @cached_property
    def _create_ex(self): return CreateRegistrant(self)

    def __repr__(self): return str(self)
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        started_at = self.started_at and "%s +%s" % (time(self.started_at,self.timezone).strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        ended_at = self.ended_at and "%s +%s" % (time(self.ended_at,self.timezone).strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        registered_at = self.registered_at and "%s +%s" % (time(self.registered_at,self.timezone).strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        return u"%s[%s] %s (%s %s) %s [ %s ] (%s - %s) :%s =%s" % (self.started_at and 'A' or 'R', self.key, self.email, self.first_name, self.last_name, self.duration, self.status or '?', started_at, ended_at, registered_at, self.join_url)

    @property
    def timezone(self): return self.session and self.session.timezone or self.webinar and self.webinar.timezone

    @classmethod
    def random(kls, webinar, count=None):
        registrants = []
        for i in xrange(count or 1):
            guid = ''.join(str(uuid4()).split('-'))
            registrants.append( Registrant(
                    webinar=webinar, 
                    first_name = u'John %s <>&\xfc\u2603 ' % guid[:8],
                    last_name = u'Smith %s <>&\xfc\u2603 ' % guid[8:16],
                    email = u'%s.%s@%s.com' % (guid[:8].upper(),guid[:8:16],guid[16:])))
        return count is None and registrants[0] or registrants
        

class RegistrantExchange(JsonExchange):
    def __init__(self, registrant, **kwargs):
        super(RegistrantExchange, self).__init__(registrant.webinar.organizer, **kwargs)
        self.registrant = registrant

class CreateRegistrant(RegistrantExchange):
    method = 'post'
    def sub_path(self): return 'webinars/%s/registrants'%self.registrant.webinar.key
    def python_data(self):
        return { "firstName": self.registrant.first_name, "lastName": self.registrant.last_name, "email": self.registrant.email }
    def process_data(self, data, response): 
        return self.registrant.merge(Registrant(**data))
    def process_error(self, error, response):
        return response is not None and response.status_code==409  # just telling us that the registrant already exists-- so it was successful


