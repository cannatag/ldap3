"""
"""

# Created on 2013.07.31
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2025 Giovanni Cannata
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

from test.config import test_base, random_id, get_connection, drop_connection, add_user, test_server_type, test_name_attr

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'controls-1', attributes={'givenName': 'given name-1'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'controls-2', attributes={'givenName': 'given name-2'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'controls-3', attributes={'givenName': 'given name-3'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_with_controls(self):
        if test_server_type == 'EDIR':
            controls = list()
            controls.append(('2.16.840.1.113719.1.27.103.7', True, 'sn'))  # grouping [Novell]
            result = self.connection.search(test_base, '(' + test_name_attr + '=' + testcase_id + 'controls-*)', attributes=['sn', 'givenName'], controls=controls)
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result

            self.assertTrue(result['description'] in ['success', 'operationsError'])
