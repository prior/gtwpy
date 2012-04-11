from utils.dict import mget,getdict,merge
from utils.obj import kwargs_str
from utils.property import cached_property, is_cached, cached_value, cached_key
from utils.string import cutoff
from .session import Session
from giftwrap import JsonExchange
from .registrant import Registrant
from .base import Base


class Webinar(Base):
    def __init__(self, organizer, **kwargs):
        super(Webinar, self).__init__()
        self.organizer = organizer
        self.key = mget(kwargs,'key','webinarKey')
        self.subject = mget(kwargs,'subject','name')
        self.description = kwargs.get('description')
        self.timezone = mget(kwargs, 'timezone', 'timeZone') or 'UTC'
        if kwargs.has_key('sessions'): self.sessions = kwargs['sessions']
        if kwargs.has_key('registrations'): self.registrations = kwargs['registrations']
        if kwargs.has_key('times') and not is_cached(self,'sessions'):
            extras = getdict(kwargs, 'scheduled','actual')
            self.sessions = [Session(webinar=self, **merge(span,extras)) for span in kwargs.get('times',[])]

    def __repr__(self): 
        return "Webinar(%s)" % kwargs_str(self,attrs=['organizer','key','subject','description'],cached=['sessions','registrations'])
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        webinar_key = self.key or '?'
        subject = self.subject or '?'
        description = cutoff(self.description or '?', 40)
        sessions = "\n  ".join(['']+[unicode(s) for s in cached_value(self,'sessions',[])])
        registrations = "\n  ".join(['']+[unicode(s) for s in cached_value(self,'registrations',[])])
        return u"W[%s]%s{%s} +%s%s%s" % (webinar_key, subject, description, self.timezone, registrations, sessions) 

    def merge(self, webinar):
        self.merge_primitives(webinar)
        self._merge_cached_exchange_collection(webinar, 'registrations', keys=[('email','status')])
        self._merge_cached_exchange_collection(webinar, 'sessions', keys=['key','starts_at','started_at'], session_match=True)
        return self

    def merge_primitives(self, webinar):
        return self._merge_primitives(webinar, 'organizer','key','subject','description')
        if webinar.timezone and webinar.timezone != 'UTC': self.timezone = webinar.timezone


    #TODO: deal with scenario where times are equal but timezones are different -- what should we do?
    def __cmp__(self, other): return self._cmp_components(other, cached_key('sessions'), 'key', 'subject', 'description', 'timezone', cached_key('registrations'))

    def clone(self):
        return Webinar(None).merge(self)

    @cached_property
    def sessions(self): return self._sessions_ex.result

    @cached_property
    def registrations(self): 
        return self._registrations_ex.result

    @cached_property
    def registrants(self): 
        uniques = {}
        for r in self.registrations:
            if r.status in ('DELETED','DENIED') or not r.email: continue
            uniques.setdefault(r.email,{})[r.status if r.status in ('APPROVED','WAITING','UNREGISTERED') else 'OTHER'] = r  # future proofing a bit
        final = [] # to keep original ordering
        for r in self.registrations:
            if uniques.get(r.email,None):
                rh = uniques.pop(r.email)
                r = rh.get('APPROVED') or rh.get('WAITING') or rh.get('UNREGISTERED') or rh.get('OTHER') or None
                if r: final.append(r)
        return final


    @cached_property
    def _sessions_ex(self): return GetSessions(self)

    @cached_property
    def _registrations_ex(self): return GetRegistrations(self)

    
class WebinarExchange(JsonExchange):
    def __init__(self, webinar, **kwargs):
        super(WebinarExchange, self).__init__(webinar.organizer, **kwargs)
        self.webinar = webinar

class GetSessions(WebinarExchange):
    def sub_path(self): return 'webinars/%s/sessions'%self.webinar.key
    def process_data(self, data, response): 
        sessions = []
        for kwargs in data:
            webinar_key = kwargs.pop('webinarKey')
            if webinar_key != self.webinar.key: raise ValueError('somethings not right here')
            sessions.append(Session(self.webinar, actual=True, **kwargs))
        return sessions

# can have multiple status values for a single email -- i.e. DELETE then WAITING
class GetRegistrations(WebinarExchange):
    def sub_path(self): return 'webinars/%s/registrants'%self.webinar.key
    def process_data(self, data, response): 
        return [Registrant(webinar=self.webinar,**kwargs) for kwargs in data]

