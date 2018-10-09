import unittest
from datetime import timedelta

from ldap3.protocol.formatters.formatters import format_ad_timedelta


class TestFormatters(unittest.TestCase):
    def test_format_ad_timedelta_thirty_mins(self):
        self.assertEqual(format_ad_timedelta(-18000000000), timedelta(minutes=30))

    def test_format_ad_timedelta_one_day(self):
        self.assertEqual(format_ad_timedelta(-864000000000), timedelta(days=1))
