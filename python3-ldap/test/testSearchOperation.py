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
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password, authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testSearchExactMatch(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(cn=test-add)', attributes = ['cn', 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), 1)

    def testSearchExtensibleMatch(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(&(o:dn:=test)(objectclass=inetOrgPerson))', attributes = ['cn', 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertGreater(len(self.connection.response), 14)

    def testSearchPresent(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(objectClass=*)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['cn', 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertGreater(len(self.connection.response), 16)

    def testSearchSubstringMany(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(sn=t*)', attributes = ['cn', 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertGreater(len(self.connection.response), 10)

    def testSearchSubstringOne(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(cn=*d)', attributes = ['cn', 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertEqual(len(self.connection.response), 1)

    def testSearchRaw(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(cn=*)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['cn', 'givenName', 'photo'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertGreater(len(self.connection.response), 14)

    def testSearchWithOperationalAttributes(self):
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(cn=test-add)', searchScope = SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['cn', 'givenName', 'photo'], getOperationalAttributes = True)
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(self.connection.response[0]['attributes']['entryDN'][0], 'cn=test-add,o=test')

    def testSearchSimplePaged(self):
        pagedSize = 1
        totalEntries = 0
        result = self.connection.search(searchBase = 'o=test', searchFilter = '(objectClass=*)', searchScope= SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['cn', 'givenName'], pagedSize = 1)
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')
        self.assertEqual(len(self.connection.response), pagedSize)
        totalEntries += len(self.connection.response)
        cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        while cookie:
            pagedSize += 1
            result = self.connection.search(searchBase = 'o=test', searchFilter = '(objectClass=*)', searchScope= SEARCH_SCOPE_WHOLE_SUBTREE, attributes = ['cn', 'givenName'], pagedSize = pagedSize, pagedCookie = cookie)
            if not isinstance(result, bool):
                self.connection.getResponse(result)
            self.assertEqual(self.connection.result['description'], 'success')
            totalEntries += len(self.connection.response)
            self.assertLessEqual(len(self.connection.response), pagedSize)
            cookie = self.connection.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        self.assertGreater(totalEntries, 18)