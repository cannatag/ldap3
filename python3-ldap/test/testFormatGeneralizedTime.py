# """
# Created on 2014.07.14
#
# @author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime

import unittest

from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, \
    test_base, dn_for_test, test_name_attr, test_lazy_connection, test_get_info, test_pooling_strategy,\
    test_pooling_active, test_pooling_exhaust, test_server_mode
from ldap3 import Server, Connection, ServerPool, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_REUSABLE_THREADED
from ldap3.protocol.formatters.formatters import format_time
from ldap3.core.timezone import OffsetTzInfo


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(test_server, pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=True)
        result = self.connection.add(dn_for_test(test_base, 'test-checked-attributes'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-checked-attributes', 'loginGraceLimit': 10})
        if not isinstance(result, bool):
            self.connection.get_response(result)

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_format_time(self):
        self.assertEqual(format_time(b'20140102030405Z'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'201401020304Z'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'2014010203.0Z'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'201401020304.1Z'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'20140102030405.2Z'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'2014010203Z'),  b'2014010203Z')
        self.assertEqual(format_time(b'20140102030405'),  b'20140102030405')
        self.assertEqual(format_time(b'201401020304'),  b'201401020304')
        self.assertEqual(format_time(b'2014010203.0'), b'2014010203.0')
        self.assertEqual(format_time(b'201401020304.1'), b'201401020304.1')
        self.assertEqual(format_time(b'20140102030405.2'), b'20140102030405.2')
        self.assertEqual(format_time(b'2014010203'),  b'2014010203')

        self.assertEqual(format_time(b'20140102030405+01'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304+01'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203.0+01'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304.1+01'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'20140102030405.2+01'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203+01'),  b'2014010203+01')
        self.assertEqual(format_time(b'20140102030405-01'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304-01'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203.0-01'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304.1-01'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'20140102030405.2-01'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203-01'),  b'2014010203-01')

        self.assertEqual(format_time(b'20140102030405+0100'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304+0100'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203.0+0100'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304.1+0100'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'20140102030405.2+0100'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203+0100'),  b'2014010203+0100')
        self.assertEqual(format_time(b'20140102030405-0100'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304-0100'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203.0-0100'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304.1-0100'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'20140102030405.2-0100'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203-0100'),  b'2014010203-0100')

        self.assertEqual(format_time(b'20140102030405+0130'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'201401020304+0130'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'2014010203.0+0130'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'201401020304.1+0130'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'20140102030405.2+0130'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'2014010203+0130'),  b'2014010203+0130')
        self.assertEqual(format_time(b'20140102030405-0130'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'201401020304-0130'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'2014010203.0-0130'), datetime(2014, 1, 2, 3, 0, 0, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'201401020304.1-0130'), datetime(2014, 1, 2, 3, 4, 6, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'20140102030405.2-0130'), datetime(2014, 1, 2, 3, 4, 5, 200000, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'2014010203-0130'),  b'2014010203-0130')