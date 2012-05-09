from sanetime import time

class Session(object):
    @property
    def starts_at(self): return self._starts_at or self._started_at
    @starts_at.setter
    def starts_at(self, starts_at): self._starts_at = starts_at
    
    @property
    def ends_at(self): return self._ends_at or self._ended_at
    @ends_at.setter
    def ends_at(self, ends_at): self._ends_at = ends_at

    @property
    def started_at(self): return self._started_at or self._starts_at
    @started_at.setter
    def started_at(self, started_at): self._started_at = started_at

    @property
    def ended_at(self): return self._ended_at or self._ends_at
    @ended_at.setter
    def ended_at(self, ended_at): self._ended_at = ended_at

    @property
    def scheduled_duration(self): return self._starts_at and self._ends_at and (self._ends_at-self._starts_at)
    @scheduled_duration.setter
    def scheduled_duration(self, delta):
        if self._starts_at: self._ends_at = self._starts_at + delta
        elif self._ends_at: self._starts_at = self._ends_at - delta

    @property
    def actual_duration(self): return self._started_at and self._ended_at and (self._ended_at-self._started_at)
    @actual_duration.setter
    def actual_duration(self, delta):
        if self._started_at: self._ended_at = self._started_at + delta
        elif self._ended_at: self._started_at = self._ended_at - delta

    @property
    def timezone(self): return getattr(self.webinar,'timezone',None) or 'UTC'

    @property
    def tz_starts_at(self): return time(self.starts_at, tz=self.timezone)
    @property
    def tz_ends_at(self): return time(self.ends_at, tz=self.timezone)
    @property
    def tz_started_at(self): return time(self.started_at, tz=self.timezone)
    @property
    def tz_ended_at(self): return time(self.ended_at, tz=self.timezone)

    def overlaps(self, other): return self.starts_at < other.ends_at and self.ends_at > other.starts_at or self.started_at < other.ended_at and self.ended_at > other.started_at

