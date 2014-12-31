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

import unittest
from ldap3 import GET_ALL_INFO

from test import test_base, \
    test_name_attr, random_id, get_connection, add_user, drop_connection

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(check_names=True, get_info=GET_ALL_INFO)
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'checked-attributes-1', attributes={'loginGraceLimit': 10}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_checked_attributes(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'checked-attributes-1*)', attributes=[test_name_attr, 'sn', 'jpegPhoto', 'loginGraceLimit'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['attributes']['sn'][0], 'checked-attributes-1')
        self.assertEqual(response[0]['attributes']['loginGraceLimit'], 10)
        if str != bytes:  # python3
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], str))
        else:  # python2
            self.assertTrue(isinstance(response[0]['attributes']['sn'][0], unicode))
        self.assertTrue(isinstance(response[0]['attributes']['loginGraceLimit'], int))

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
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'checked-attributes-1*)', attributes=[test_name_attr, 'sn', 'jpegPhoto', 'loginGraceLimit'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        self.assertTrue('CHECKED-ATTRIBUTES-1' in response[0]['attributes']['cn'][0])
        self.assertEqual(response[0]['attributes']['sn'][0], '1-setubirtta-dekcehc')
        self.assertEqual(response[0]['attributes']['loginGraceLimit'], 1010)
