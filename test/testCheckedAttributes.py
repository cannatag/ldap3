"""
"""

# Created on 2014.07.14
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2025 Giovanni Cannata
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

import unittest

from ldap3 import ALL
from test.config import test_base, test_name_attr, random_id, get_connection, add_user, drop_connection, test_int_attr, test_server_type, get_response_values

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection(check_names=True, get_info=ALL)
        self.delete_at_teardown = []
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'chk-1', attributes={'loginGraceLimit': 0}))
        elif test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'chk-1'))
        else:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'chk-1'))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_checked_attributes(self):
        status, result, response, request = get_response_values(self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'chk-1*)', attributes=[test_name_attr, 'sn', test_int_attr]), self.connection)
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes']['sn'], 'chk-1')  # sn is single-value in Active Directory
        else:
            self.assertEqual(response[0]['attributes']['sn'][0], 'chk-1')
        self.assertEqual(response[0]['attributes'][test_int_attr], 0)
        if str != bytes:  # python3
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], str))
        else:  # python2
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], unicode))
        self.assertTrue(isinstance(response[0]['attributes'][test_int_attr], int))

    def test_custom_formatter(self):
        def to_upper(byte_value):
            if str != bytes:  # python 3
                return str(byte_value, encoding='UTF-8').upper()
            else:
                return unicode(byte_value, encoding='UTF-8').upper()
        if str != bytes:  # python3
            formatter = {'cn': to_upper,  # name to upper
                         '2.5.4.4': lambda v: str(v, encoding='UTF-8')[::-1],  # sn reversed
                         '1.3.6.1.4.1.1466.115.121.1.27': lambda v: int(v) + 1000}  # integer syntax incremented by 1000
        else:
            formatter = {'cn': to_upper,  # name to upper
                         '2.5.4.4': lambda v: unicode(v, encoding='UTF-8')[::-1],  # sn reversed
                         '1.3.6.1.4.1.1466.115.121.1.27': lambda v: int(v) + 1000}  # integer syntax incremented by 1000
        self.connection.server.custom_formatter = formatter
        status, result, response, request  = get_response_values(self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'chk-1*)', attributes=[test_name_attr, 'sn', test_int_attr]), self.connection)
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertTrue('CHK-1' in response[0]['attributes']['cn'])  # cn is single-valued in Active Directory
            self.assertEqual(response[0]['attributes']['sn'], '1-khc')  # sn is single-valued in Active Directory
        else:
            self.assertTrue('CHK-1' in response[0]['attributes']['cn'][0])
            self.assertEqual(response[0]['attributes']['sn'][0], '1-khc')
        self.assertEqual(response[0]['attributes'][test_int_attr], 1000)
