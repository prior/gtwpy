from utils.dict import mget
from utils.string import nstrip
from utils.property import cached_property
from sanetime import nsanetime, sanedelta, sanetztime
from .base import Base
from giftwrap import JsonExchange


class Registrant(Base):
    def __init__(self, **kwargs):
        super(Registrant, self).__init__()
        self.webinar = kwargs.get('webinar')
        self.session = kwargs.get('session')
        self.key = mget(kwargs, 'key', 'registrant_key', 'registrantKey')
        self.email = mget(kwargs, 'email', 'attendeeEmail')
        self.first_name = mget(kwargs, 'first_name', 'firstName', 'first')
        self.last_name = mget(kwargs, 'last_name', 'lastName', 'last')
        if kwargs.get('name'): self.name = nstrip(kwargs.get('name'))
        self.registered_at = nsanetime(mget(kwargs, 'registered_at', 'registrationDate'))
        self.join_url = mget(kwargs, 'join_url', 'joinUrl')
        self.status = kwargs.get('status')
        self.duration = kwargs.get('duration') or kwargs.get('attendanceTimeInSeconds') and sanedelta(s=kwargs['attendanceTimeInSeconds'])

    @property
    def name(self): return ('%s %s' % (self.first_name or '', self.last_name or '')).strip()
    @name.setter
    def name(self, n):
        parts = n.split(' ')
        self.first_name = self.first_name or ' '.join(parts[0:-1]).strip() or None
        self.last_name = self.last_name or parts[-1].strip() or None

    @property
    def started_at(self): return self.session and self.session.key and self.duration and self.session.started_at

    @property
    def ended_at(self): 
        return self.session and self.session.key and self.duration and self.session.started_at+self.duration

    def merge(self, other):
        self._merge_primitives(other, 'webinar', 'session', 'key', 'email', 'first_name', 'last_name', 'registered_at', 'join_url', 'status', 'duration')
        return self

    def __cmp__(self, other): return self._cmp_components(other, 'email', 'last_name', 'first_name', 'started_at', 'ended_at', 'key', 'registered_at', 'join_url', 'status', 'duration')

    def clone(self): return Registrant().merge(self)

    def create(self): return self._create_ex.result

    @classmethod
    def _create(kls, registrants): return CreateRegistrant.async_results([r._create_ex for r in registrants])

    @cached_property
    def _create_ex(self): return CreateRegistrant(self)

    def __repr__(self): return str(self)
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        started_at = self.started_at and "%s +%s" % (sanetztime(self.started_at).set_tz(self.timezone).strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        ended_at = self.ended_at and "%s +%s" % (sanetztime(self.ended_at).set_tz(self.timezone).strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        registered_at = self.registered_at and "%s +%s" % (sanetztime(self.registered_at).set_tz(self.timezone).strftime('%m/%d/%y %I:%M%p').lower(), self.timezone) or '?'
        return u"%s[%s] %s (%s %s) %s [ %s ] (%s - %s) :%s =%s" % (self.started_at and 'A' or 'R', self.key, self.email, self.first_name, self.last_name, self.duration, self.status or '?', started_at, ended_at, registered_at, self.join_url)

    @property
    def timezone(self): return self.session and self.session.timezone or self.webinar and self.webinar.timezone
        

class RegistrantExchange(JsonExchange):
    def __init__(self, registrant, **kwargs):
        super(RegistrantExchange, self).__init__(registrant.webinar.organizer, **kwargs)
        self.registrant = registrant

class CreateRegistrant(RegistrantExchange):
    method = 'post'
    def sub_path(self): return 'webinars/%s/registrants'%self.webinar.key
    def python_data(self):
        return { "firstName": self.registrant.first_name, "lastName": self.registrant.last_name, "email": self.registrant.email }
    def process_data(self, data, response): 
        return self.registrant.merge(Registrant(**data))


