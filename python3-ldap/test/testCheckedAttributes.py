"""
Created on 2014.07.14

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""
from datetime import datetime

import unittest

from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, test_dn_builder, test_name_attr, test_lazy_connection, test_get_info, test_check_names
from ldap3 import Server, Connection, SEARCH_SCOPE_WHOLE_SUBTREE, STRATEGY_REUSABLE_THREADED, GET_ALL_INFO
from ldap3.protocol.convert import format_time, OffsetTzInfo


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_ALL_INFO)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=True)
        result = self.connection.add(test_dn_builder(test_base, 'test-checked-attributes'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-checked-attributes', 'loginGraceLimit': 10})
        if not isinstance(result, bool):
            self.connection.get_response(result)

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_search_checked_attributes(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=test-checked-attributes)', attributes=[test_name_attr, 'sn', 'jpegPhoto', 'loginGraceLimit'])
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['attributes']['sn'][0], 'test-checked-attributes')
        self.assertEqual(response[0]['attributes']['loginGraceLimit'], 10)
        if str != bytes:  # python3
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], str))
        else:  # python2
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], unicode))
        self.assertTrue(isinstance(response[0]['attributes']['loginGraceLimit'], int))

    def test_format_time(self):
        self.assertEqual(format_time(b'20140102030405Z'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'201401020304Z'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(0, 'UTC')))
        self.assertEqual(format_time(b'2014010203Z'),  b'2014010203Z')
        self.assertEqual(format_time(b'20140102030405'),  b'20140102030405')
        self.assertEqual(format_time(b'201401020304'),  b'201401020304')
        self.assertEqual(format_time(b'2014010203'),  b'2014010203')

        self.assertEqual(format_time(b'20140102030405+01'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304+01'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203+01'),  b'2014010203+01')
        self.assertEqual(format_time(b'20140102030405-01'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304-01'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203-01'),  b'2014010203-01')

        self.assertEqual(format_time(b'20140102030405+0100'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'201401020304+0100'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(60, 'UTC+01')))
        self.assertEqual(format_time(b'2014010203+0100'),  b'2014010203+0100')
        self.assertEqual(format_time(b'20140102030405-0100'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'201401020304-0100'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-60, 'UTC-01')))
        self.assertEqual(format_time(b'2014010203-0100'),  b'2014010203-0100')

        self.assertEqual(format_time(b'20140102030405+0130'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'201401020304+0130'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(90, 'UTC+0130')))
        self.assertEqual(format_time(b'2014010203+0130'),  b'2014010203+0130')
        self.assertEqual(format_time(b'20140102030405-0130'), datetime(2014, 1, 2, 3, 4, 5, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'201401020304-0130'), datetime(2014, 1, 2, 3, 4, 0, 0, OffsetTzInfo(-90, 'UTC-0130')))
        self.assertEqual(format_time(b'2014010203-0130'),  b'2014010203-0130')

    def test_custom_formatter(self):
        def to_upper(byte_value):
            if str != bytes:
                return str(byte_value, encoding='UTF-8').upper()
            else:
                return unicode(byte_value, encoding='UTF-8').upper()
        if str != bytes:  # python3
            formatter = {'cn': to_upper,  # name to upper
                         '2.5.4.4': lambda v: str(v, encoding='UTF-8')[::-1],  # sn reversed
                         '1.3.6.1.4.1.1466.115.121.1.27': lambda v: int(v) + 1000  # integer syntax incremented by 1000
            }
        else:
            formatter = {'cn': to_upper,  # name to upper
                         '2.5.4.4': lambda v: unicode(v, encoding='UTF-8')[::-1],  # sn reversed
                         '1.3.6.1.4.1.1466.115.121.1.27': lambda v: int(v) + 1000  # integer syntax incremented by 1000
            }
        self.connection.server.custom_formatter = formatter
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=test-checked-attributes)', attributes=[test_name_attr, 'sn', 'jpegPhoto', 'loginGraceLimit'])
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['attributes']['cn'][0], 'TEST-CHECKED-ATTRIBUTES')
        self.assertEqual(response[0]['attributes']['sn'][0], 'setubirtta-dekcehc-tset')
        self.assertEqual(response[0]['attributes']['loginGraceLimit'], 1010)