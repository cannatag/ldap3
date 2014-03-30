"""
Created on 2013.06.06

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

import unittest

from ldap3.core.server import Server
from ldap3.core.connection import Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, test_dn_builder, test_name_attr, test_lazy_connection
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True))
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection)
        self.connection.add(test_dn_builder(test_base, 'test-search-(parentheses)'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-search-(parentheses)'})

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def test_search_exact_match(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=test-add-operation)', attributes=[test_name_attr, 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), 1)

    def test_search_extensible_match(self):
        result = self.connection.search(search_base=test_base, search_filter='(&(o:dn:=test)(objectclass=inetOrgPerson))', attributes=[test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertTrue(len(self.connection.response) > 8)

    def test_search_present(self):
        result = self.connection.search(search_base=test_base, search_filter='(objectClass=*)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, attributes=[test_name_attr, 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertTrue(len(self.connection.response) > 9)

    def test_search_substring_many(self):
        result = self.connection.search(search_base=test_base, search_filter='(sn=t*)', attributes=[test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertTrue(len(self.connection.response) > 8)

    def test_search_substring_one(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=*y)', attributes=[test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertTrue(len(self.connection.response) > 1)

    def test_search_raw(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=*)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, attributes=[test_name_attr, 'givenName', 'photo'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertTrue(len(self.connection.response) > 8)

    def test_search_with_operational_attributes(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=test-add-operation)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, attributes=[test_name_attr, 'givenName', 'photo'], get_operational_attributes=True)
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(self.connection.response[0]['attributes']['entryDN'][0], test_dn_builder(test_base, 'test-add-operation'))

    def test_search_simple_paged(self):
        paged_size = 1
        total_entries = 0
        result = self.connection.search(search_base=test_base, search_filter='(objectClass=*)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, attributes=[test_name_attr, 'givenName'], paged_size=paged_size)
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), paged_size)
        total_entries += len(self.connection.response)
        cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        while cookie:
            paged_size += 1
            result = self.connection.search(search_base=test_base, search_filter='(objectClass=*)', search_scope=SEARCH_SCOPE_WHOLE_SUBTREE, attributes=[test_name_attr, 'givenName'], paged_size=paged_size, paged_cookie=cookie)
            if not isinstance(result, bool):
                self.connection.get_response(result)
            self.assertEqual(self.connection.result['description'], 'success')
            total_entries += len(self.connection.response)
            self.assertTrue(len(self.connection.response) <= paged_size)
            cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        self.assertTrue(total_entries > 9)

    def test_search_exact_match_with_parentheses_in_filter(self):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + r'=*\29*)', attributes=[test_name_attr, 'sn'])
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), 1)
        self.assertEqual(self.connection.response[0]['attributes']['cn'][0], 'test-search-(parentheses)')
