"""
"""

# Created on 2014.05.01
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2020 Giovanni Cannata
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
from ldap3.core.exceptions import LDAPAttributeError, LDAPObjectClassError
from test.config import test_base, generate_dn, test_name_attr, random_id, get_connection, add_user, drop_connection

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection(check_names=True, get_info=ALL)
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_wrong_assertion(self):
        if not self.connection.strategy.pooled:
            self.assertRaises(LDAPAttributeError, self.connection.search, search_base=test_base, search_filter='(xxx=yyy)', attributes=[test_name_attr])

    def test_wrong_attribute(self):
        if not self.connection.strategy.pooled:
            self.assertRaises(LDAPAttributeError, self.connection.search, search_base=test_base, search_filter='(cn=yyy)', attributes=[test_name_attr, 'xxx'])

    def test_wrong_object_class_add(self):
        if not self.connection.strategy.pooled:
            self.assertRaises(LDAPObjectClassError, self.connection.add, generate_dn(test_base, testcase_id, 'test-add-operation-wrong'), 'inetOrgPerson', {'objectClass': ['inetOrgPerson', 'xxx'], 'sn': 'test-add', test_name_attr: 'test-add-operation'})

    def test_valid_assertion(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'chk-1'))

        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'chk-1)', attributes=[test_name_attr])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)

    def test_valid_attribute(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'chk-2', attributes={'givenName': 'given-name-2'}))
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'chk-2)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)

    def test_valid_object_class_add(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'chk-3', attributes={'objectClass': ['inetOrgPerson', 'Person']}))
        self.assertEqual(self.delete_at_teardown[0][1]['description'], 'success')
