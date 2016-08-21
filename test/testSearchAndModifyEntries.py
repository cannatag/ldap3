"""
"""

# Created on 2016.08.20
#
# Author: Giovanni Cannata
#
# Copyright 2015, 2016 Giovanni Cannata
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

from test import test_base, test_name_attr, random_id, get_connection, \
    add_user, drop_connection, test_server_type, test_int_attr

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-1', attributes={'givenName': 'givenname-1', test_int_attr: 0}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-2', attributes={'givenName': 'givenname-2', test_int_attr: 0}))
        elif test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-2', attributes={'givenName': 'givenname-2'}))
        else:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-2', attributes={'givenName': 'givenname-2'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_and_add_value_to_multivalue(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-and-modify-1)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
            entries = self.connection._get_entries(response)
        else:
            result = self.connection.result
            entries = self.connection.entries
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(entries), 1)
        writable_entry = entries[0].make_writable('inetorgperson')
        writable_entry.givenname.add_value('added-givenname-1')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertEqual(writable_entry.givenname, ['givenname-1', 'added-givenname-1'])

    def test_search_and_add_value_to_single_valued(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-and-modify-1)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
            entries = self.connection._get_entries(response)
        else:
            result = self.connection.result
            entries = self.connection.entries
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(entries), 1)
        writable_entry = entries[0].make_writable('inetorgperson')
        writable_entry.preferredDeliveryMethod.add_value('any')  # single valued in organizationalPerson, defined in rfc4519
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertEqual(writable_entry.preferredDeliveryMethod, 'any')
