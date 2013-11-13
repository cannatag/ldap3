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
from ldap3.server import Server
from ldap3.connection import Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, testDnBuilder, test_name_attr
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                     authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testSearchExactMatch(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(' + test_name_attr + '=test-add-operation)', attributes = [test_name_attr, 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), 1)

    def testSearchExtensibleMatch(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(&(o:dn:=test)(objectclass=inetOrgPerson))',
                                        attributes = [test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertGreater(len(self.connection.response), 8)

    def testSearchPresent(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(objectClass=*)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                                        attributes = [test_name_attr, 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertGreater(len(self.connection.response), 9)

    def testSearchSubstringMany(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(sn=t*)', attributes = [test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertGreater(len(self.connection.response), 8)

    def testSearchSubstringOne(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(' + test_name_attr + '=*y)', attributes = [test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertGreater(len(self.connection.response), 1)

    def testSearchRaw(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(' + test_name_attr + '=*)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                                        attributes = [test_name_attr, 'givenName', 'photo'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertGreater(len(self.connection.response), 8)

    def testSearchWithOperationalAttributes(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(' + test_name_attr + '=test-add-operation)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                                        attributes = [test_name_attr, 'givenName', 'photo'], getOperationalAttributes = True)
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(self.connection.response[0]['attributes']['entryDN'][0], testDnBuilder(test_base, 'test-add-operation'))

    def testSearchSimplePaged(self):
        pagedSize = 1
        totalEntries = 0
        result = self.connection.search(searchBase = test_base, searchFilter = '(objectClass=*)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                                        attributes = [test_name_attr, 'givenName'], pagedSize = pagedSize)
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), pagedSize)
        totalEntries += len(self.connection.response)
        cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        while cookie:
            pagedSize += 1
            result = self.connection.search(searchBase = test_base, searchFilter = '(objectClass=*)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE,
                                            attributes = [test_name_attr, 'givenName'], pagedSize = pagedSize, pagedCookie = cookie)
            if not isinstance(result, bool):
                self.connection.getResponse(result)
            self.assertEqual(self.connection.result['description'], 'success')
            totalEntries += len(self.connection.response)
            self.assertLessEqual(len(self.connection.response), pagedSize)
            cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        self.assertGreater(totalEntries, 9)
