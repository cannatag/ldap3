# """
# Created on 2014.07.14
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
import unittest

from ldap3.protocol.formatters.formatters import format_time
from ldap3.core.timezone import OffsetTzInfo


class Test(unittest.TestCase):
    def test_format_time(self):
        self.assertEqual(format_time(b'20140102030405Z'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'201401020304Z'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'2014010203.0Z'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'201401020304.1Z'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'20140102030405.2Z'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'2014010203Z'), b'2014010203Z')
        self.assertEqual(format_time(b'20140102030405'), b'20140102030405')
        self.assertEqual(format_time(b'201401020304'), b'201401020304')
        self.assertEqual(format_time(b'2014010203.0'), b'2014010203.0')
        self.assertEqual(format_time(b'201401020304.1'), b'201401020304.1')
        self.assertEqual(format_time(b'20140102030405.2'), b'20140102030405.2')
        self.assertEqual(format_time(b'2014010203'), b'2014010203')

        self.assertEqual(format_time(b'20140102030405+01'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304+01'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203.0+01'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304.1+01'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'20140102030405.2+01'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203+01'), b'2014010203+01')
        self.assertEqual(format_time(b'20140102030405-01'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304-01'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203.0-01'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304.1-01'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'20140102030405.2-01'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203-01'), b'2014010203-01')

        self.assertEqual(format_time(b'20140102030405+0100'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304+0100'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203.0+0100'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304.1+0100'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'20140102030405.2+0100'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203+0100'), b'2014010203+0100')
        self.assertEqual(format_time(b'20140102030405-0100'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304-0100'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203.0-0100'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304.1-0100'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'20140102030405.2-0100'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203-0100'), b'2014010203-0100')

        self.assertEqual(format_time(b'20140102030405+0130'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'201401020304+0130'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'2014010203.0+0130'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'201401020304.1+0130'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'20140102030405.2+0130'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'2014010203+0130'), b'2014010203+0130')
        self.assertEqual(format_time(b'20140102030405-0130'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'201401020304-0130'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'2014010203.0-0130'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'201401020304.1-0130'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'20140102030405.2-0130'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'2014010203-0130'), b'2014010203-0130')
