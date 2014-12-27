from datetime import timedelta, tzinfo


# from python standard library docs
class OffsetTzInfo(tzinfo):
    """Fixed offset in minutes east from UTC"""

    def __init__(self, offset, name):
        self.offset = offset
        self.name = name
        self._offset = timedelta(minutes=offset)
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):

        return 'OffsetTzInfo(offset={0.offset!r}, name={0.name!r})'.format(self)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return timedelta(0)