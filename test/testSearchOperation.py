# -*- coding: cp850 -*-
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

from ldap3.utils.conv import escape_bytes, escape_filter_chars
from test import test_base, test_name_attr, random_id, get_connection, \
    add_user, drop_connection, test_server_type, test_int_attr
from ldap3 import SUBTREE

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1', test_int_attr: 0}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2', test_int_attr: 0}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, u'search-3-\u2122', attributes={'givenName': 'givenname-3', test_int_attr: 0}))  # TRADE-MARK SIGN
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, u'search-4-Öäçïó', attributes={'givenName': 'givenname-4', test_int_attr: 0}))
        elif test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, u'search-3-\u2122', attributes={'givenName': 'givenname-3'}))  # TRADE-MARK SIGN
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, u'search-4-Öäçïó', attributes={'givenName': 'givenname-4', test_int_attr: 0}))
        else:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, u'search-3-\u2122', attributes={'givenName': 'givenname-3'}))  # TRADE-MARK SIGN
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, u'search-4-Öäçïó', attributes={'givenName': 'givenname-4', test_int_attr: 0}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_exact_match(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-1)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes']['givenName'], 'givenname-1')
        else:
            self.assertEqual(response[0]['attributes']['givenName'][0], 'givenname-1')

    def test_search_extensible_match(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.search(search_base=test_base, search_filter='(&(ou:dn:=fixtures)(objectclass=inetOrgPerson))', attributes=[test_name_attr, 'givenName', 'sn'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
                result = self.connection.result
            self.assertEqual(result['description'], 'success')
            self.assertTrue(len(response) >= 2)

    def test_search_present(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=*)', search_scope=SUBTREE, attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(len(response) >= 2)

    def test_search_substring_many(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + '*)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 4)

    def test_search_with_operational_attributes(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-1)', search_scope=SUBTREE, attributes=[test_name_attr, 'givenName'], get_operational_attributes=True)
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        if self.connection.check_names:
            if test_server_type == 'AD':
                self.assertEqual(response[0]['dn'].lower(), self.delete_at_teardown[0][0].lower())
            else:
                self.assertEqual(response[0]['attributes']['entryDN'], self.delete_at_teardown[0][0])

    def test_search_simple_paged(self):
        if not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-5', attributes={'givenName': 'givenname-3'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-6', attributes={'givenName': 'givenname-4'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-7', attributes={'givenName': 'givenname-5'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-8', attributes={'givenName': 'givenname-6'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-9', attributes={'givenName': 'givenname-7'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-10', attributes={'givenName': 'givenname-8'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-11', attributes={'givenName': 'givenname-9'}))

            paged_size = 4
            total_entries = 0
            result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + '*)', search_scope=SUBTREE, attributes=[test_name_attr, 'givenName'], paged_size=paged_size)
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
                result = self.connection.result
            self.assertEqual(result['description'], 'success')
            self.assertEqual(len(response), paged_size)
            total_entries += len(response)
            cookie = result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            while cookie:
                result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + '*)', search_scope=SUBTREE, attributes=[test_name_attr, 'givenName'], paged_size=paged_size, paged_cookie=cookie)
                if not self.connection.strategy.sync:
                    response, result = self.connection.get_response(result)
                else:
                    response = self.connection.response
                    result = self.connection.result
                self.assertEqual(result['description'], 'success')
                total_entries += len(response)
                self.assertTrue(len(response) <= paged_size)
                cookie = result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            self.assertEqual(total_entries, 11)

    def test_search_exact_match_with_escaped_parentheses_in_filter(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, '(search)-12', attributes={'givenName': 'givenname-12'}))
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + '*' + escape_bytes(')') + '*)', attributes=[test_name_attr, 'sn'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes'][test_name_attr], testcase_id + '(search)-12')
        else:
            self.assertEqual(response[0]['attributes'][test_name_attr][0], testcase_id + '(search)-12')

    # def test_search_exact_match_with_parentheses_in_filter(self):
    #     self.delete_at_teardown.append(add_user(self.connection, testcase_id, '(search)-13', attributes={'givenName': 'givenname-13'}))
    #     result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + '*)*)', attributes=[test_name_attr, 'sn'])
    #     if not self.connection.strategy.sync:
    #         response, result = self.connection.get_response(result)
    #     else:
    #         response = self.connection.response
    #         result = self.connection.result
    #     self.assertEqual(result['description'], 'success')
    #     self.assertEqual(len(response), 1)
    #     if test_server_type == 'AD':
    #         self.assertEqual(response[0]['attributes'][test_name_attr], testcase_id + '(search)-13')
    #     else:
    #         self.assertEqual(response[0]['attributes'][test_name_attr][0], testcase_id + '(search)-13')

    def test_search_integer_exact_match(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_int_attr + '=0))', attributes=[test_name_attr, test_int_attr])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 4)

    def test_search_integer_less_than(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_int_attr + ' <=1))', attributes=[test_name_attr, test_int_attr])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 4)

    def test_search_integer_greater_than(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(' + test_name_attr + '=' + testcase_id + '*)(' + test_int_attr + ' >=-1))', attributes=[test_name_attr, test_int_attr])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 4)

    def test_search_not_match(self):
        result = self.connection.search(search_base=test_base,
                                        search_filter='(!(' + test_name_attr + '=' + testcase_id + 'search-1))',
                                        attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = [entry for entry in self.connection.response if entry['dn'].lower().startswith(test_name_attr.lower() + '=' + testcase_id.lower())]
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(len(response) >= 1)

    def test_search_exact_match_with_unicode_in_filter(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + u'search-3-\u2122)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes']['givenName'], 'givenname-3')
        else:
            self.assertEqual(response[0]['attributes']['givenName'][0], 'givenname-3')

    def test_search_exact_match_with_unescaped_chars(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + u'search-4-Öäçïó)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes']['givenName'], 'givenname-4')
        else:
            self.assertEqual(response[0]['attributes']['givenName'][0], 'givenname-4')

    def test_search_exact_match_with_unescaped_backslash_in_filter(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-13', attributes={'givenName': testcase_id + 'givenname\\-13'}))
        result = self.connection.search(search_base=test_base, search_filter='(givenname=' + testcase_id + '*\\*)', attributes=[test_name_attr, 'sn'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes'][test_name_attr], testcase_id + 'search-13')
        else:
            self.assertEqual(response[0]['attributes'][test_name_attr][0], testcase_id + 'search-13')

    def test_search_exact_match_with_escaped_backslash_in_filter(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-14', attributes={'givenName': testcase_id + 'givenname\\-14'}))
        result = self.connection.search(search_base=test_base, search_filter='(givenname=' + testcase_id + '*\\5c*)', attributes=[test_name_attr, 'sn'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes'][test_name_attr], testcase_id + 'search-14')
        else:
            self.assertEqual(response[0]['attributes'][test_name_attr][0], testcase_id + 'search-14')

    def test_search_exact_match_with_escape_chars_backslash_in_filter(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-15', attributes={'givenName': testcase_id + 'givenname\\-15'}))
        result = self.connection.search(search_base=test_base, search_filter='(givenname=' + testcase_id + '*' + escape_filter_chars('\\') + '*)', attributes=[test_name_attr, 'sn'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 1)
        if test_server_type == 'AD':
            self.assertEqual(response[0]['attributes'][test_name_attr], testcase_id + 'search-15')
        else:
            self.assertEqual(response[0]['attributes'][test_name_attr][0], testcase_id + 'search-15')
