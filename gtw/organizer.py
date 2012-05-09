from utils.property import cached_property
from utils.dict import mget,kwargs_str
from utils.list import sort
from giftwrap import Auth, Exchange, JsonExchange
from .webinar import Webinar
from .session import Session
from sanetime import time,delta


API_TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DEFAULT_HISTORY_DELTA = delta(my=20)
GTW_NOW_DELTA = delta(s=10) # cuz gtw 500s when your time range enters the future, and their servers seem to be off by a few seconds


class Organizer(Auth):
    domain = 'api.citrixonline.com'

    def base_path(self): return 'G2W/rest/organizers/%s' % self.key
    def headers(self): return {'Authorization': 'OAuth oauth_token=%s'%self.oauth}

    def __init__(self, **kwargs):
        super(Organizer, self).__init__()
        self.oauth = mget(kwargs,'oauth','oauth_token','access_token')
        self.key = mget(kwargs,'key','organizerKey','organizer_key')
        self.now = time()
        self.starts_at = kwargs.get('starts_at',None) or (self.now - DEFAULT_HISTORY_DELTA)

    def __repr__(self): 
        return "Organizer(%s)" % kwargs_str(self.__dict__,'oauth','key')
    def __str__(self): return unicode(self).encode('utf-8')
    def __unicode__(self):
        return u"U[%s] token=%s" % (self.key or '?', self.oauth or '?')

    @property
    def past_webinars(self): return self._past_ex.result
    @property
    def future_webinars(self): return self._future_ex.result
    @property
    def sessioned_webinars(self): return self._sessioned_ex.result

    @cached_property
    def webinars(self):
        webinars = {}
        for ex in Exchange.async_exchange([self._future_ex, self._past_ex, self._sessioned_ex]):
            for that in ex.result:
                this = webinars.get(that.key)
                if this: this.merge(that)
                else: webinars[that.key] = that
        return sort(webinars.values())

    @cached_property
    def _past_ex(self): return GetPastWebinars(self, self.starts_at, self.now-GTW_NOW_DELTA)

    @cached_property
    def _future_ex(self): return GetFutureWebinars(self)

    @cached_property
    def _sessioned_ex(self): return GetSessionedWebinars(self, self.starts_at, self.now-GTW_NOW_DELTA)



# exchanges

class TimeWindowExchange(JsonExchange):
    def __init__(self, auth, start_at, end_at, **kwargs):
        super(TimeWindowExchange, self).__init__(auth, **kwargs)
        self.start_at = start_at
        self.end_at = end_at

class GetPastWebinars(TimeWindowExchange):
    sub_path = 'historicalWebinars'
    def params(self): return { 'fromTime':self.start_at.strftime(API_TIME_FORMAT), 'toTime':self.end_at.strftime(API_TIME_FORMAT) }
    def process_data(self, data, response): return [Webinar(self.auth, scheduled=True, **kwargs) for kwargs in data]


class GetFutureWebinars(JsonExchange):
    sub_path = 'webinars'
    def process_data(self, data, response): return [Webinar(self.auth, scheduled=True, **kwargs) for kwargs in data]

class GetSessionedWebinars(TimeWindowExchange):
    sub_path = 'sessions'
    def params(self): return { 'fromTime':self.start_at.strftime(API_TIME_FORMAT), 'toTime':self.end_at.strftime(API_TIME_FORMAT) }
    def process_data(self, data, response): 
        webinars_hash = {}
        webinars = []
        for kwargs in data:
            key = kwargs.pop('webinarKey')
            webinar = webinars_hash.get(key, None)
            if not webinar:
                webinar = Webinar(self.auth, key=key, sessions=[])
                webinars.append(webinar)
                webinars_hash[key] = webinar
            webinar.sessions.append(Session(webinar, actual=True, **kwargs))
        return webinars


