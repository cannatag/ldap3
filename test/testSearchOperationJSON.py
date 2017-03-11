"""
"""

# Created on 2013.06.06
#
# Author: Giovanni Cannata
#
# Copyright 2013, 2014, 2015, 2016 Giovanni Cannata
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
import json

from ldap3 import SUBTREE
from ldap3.utils.conv import escape_bytes
from test import test_base, test_name_attr, random_id, get_connection, add_user, drop_connection, test_int_attr, test_server_type

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1', test_int_attr: 0}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2', test_int_attr: 0}))
        elif test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2'}))
        else:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_exact_match(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-1)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, _ = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()

        json_entries = json.loads(json_response)['entries']
        self.assertEqual(len(json_entries), 1)

    def test_search_extensible_match(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.search(search_base=test_base, search_filter='(&(ou:dn:=fixtures)(objectclass=inetOrgPerson))', attributes=[test_name_attr, 'givenName', 'sn'])
            if not self.connection.strategy.sync:
                response, _ = self.connection.get_response(result)
                json_response = self.connection.response_to_json(search_result=response)
            else:
                json_response = self.connection.response_to_json()

            json_entries = json.loads(json_response)['entries']
            self.assertTrue(len(json_entries) >= 2)

    def test_search_present(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=*)', search_scope=SUBTREE, attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, _ = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']
        self.assertTrue(len(json_entries) >= 2)

    def test_search_substring_many(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + '*)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, _ = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']
        self.assertEqual(len(json_entries), 2)

    def test_search_with_operational_attributes(self):
        if test_server_type == 'EDIR':
            test_operation_attribute = 'entryDN'
        elif test_server_type == 'SLAPD':
            test_operation_attribute = 'entryDN'
        else:
            test_operation_attribute = 'xxx'
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-1)', search_scope=SUBTREE, attributes=[test_name_attr, 'givenName'], get_operational_attributes=True)
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']

        if self.connection.check_names:
            if test_server_type == 'AD':
                self.assertEqual(json_entries[0]['dn'].lower(), self.delete_at_teardown[0][0].lower())
            elif test_server_type == 'SLAPD':
                self.assertEqual(json_entries[0]['attributes'][test_operation_attribute], self.delete_at_teardown[0][0])
            else:
                self.assertEqual(json_entries[0]['attributes'][test_operation_attribute], self.delete_at_teardown[0][0])

    def test_search_exact_match_with_parentheses_in_filter(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, '(search)-3', attributes={'givenName': 'givenname-3'}))
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_name_attr + '=*' + escape_bytes(')') + '*))', attributes=[test_name_attr, 'sn'])
        if not self.connection.strategy.sync:
            response, _ = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']

        self.assertEqual(len(json_entries), 1)
        if test_server_type == 'AD':
            self.assertEqual(json_entries[0]['attributes'][test_name_attr], testcase_id + '(search)-3')
        else:
            self.assertEqual(json_entries[0]['attributes'][test_name_attr][0], testcase_id + '(search)-3')

    def test_search_integer_exact_match(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_int_attr + '=0))', attributes=[test_name_attr, test_int_attr])
        if not self.connection.strategy.sync:
            response, _ = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']

        self.assertEqual(len(json_entries), 2)

    def test_search_integer_less_than(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_int_attr + ' <=1))', attributes=[test_name_attr, test_int_attr])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']

        self.assertEqual(len(json_entries), 2)

    def test_search_integer_greater_than(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_int_attr + '>=-1))', attributes=[test_name_attr, test_int_attr])
        if not self.connection.strategy.sync:
            response, _ = self.connection.get_response(result)
            json_response = self.connection.response_to_json(search_result=response)
        else:
            json_response = self.connection.response_to_json()
        json_entries = json.loads(json_response)['entries']

        self.assertEqual(len(json_entries), 2)
