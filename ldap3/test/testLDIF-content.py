# Created on 2013.12.10
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

from test import test_base, test_name_attr, get_connection, random_id, add_user, \
    drop_connection


testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'ldif-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'ldif-2'))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_single_search_result_to_ldif(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'ldif-1)', attributes=[test_name_attr, 'givenName', 'objectClass', 'sn'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response

        l = self.connection.response_to_ldif(response)
        self.assertTrue('version: 1' in l)
        self.assertTrue('dn: ' + test_name_attr + '=' + testcase_id + 'ldif-1,' + test_base in l)
        self.assertTrue('objectClass: inetOrgPerson' in l)
        self.assertTrue('objectClass: Top' in l)
        self.assertTrue(test_name_attr + ': ' + testcase_id + 'ldif-1' in l)
        self.assertTrue('sn: ldif-1' in l)
        self.assertTrue('total number of entries: 1' in l)

    def test_multiple_search_result_to_ldif(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'ldif-*)', attributes=[test_name_attr, 'givenName', 'sn', 'objectClass'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response

        l = self.connection.response_to_ldif(response)
        print(l)
        self.assertTrue('version: 1' in l)
        self.assertTrue('dn: ' + test_name_attr + '=' + testcase_id + 'ldif-1,' + test_base in l)
        self.assertTrue('objectClass: inetOrgPerson' in l)
        self.assertTrue('objectClass: Top' in l)
        self.assertTrue(test_name_attr + ': ' + testcase_id + 'ldif-1' in l)
        self.assertTrue('sn: ldif-1' in l)
        self.assertTrue('dn: ' + test_name_attr + '=' + testcase_id + 'ldif-1,' + test_base in l)
        self.assertTrue(test_name_attr + ': ' + testcase_id + 'ldif-2' in l)
        self.assertTrue('sn: ldif-2' in l)
        self.assertTrue('# total number of entries: 2' in l)
