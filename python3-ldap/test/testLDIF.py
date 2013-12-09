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


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                     authentication = test_authentication)
        result = self.connection.add(testDnBuilder(test_base, 'test-ldif'), 'iNetOrgPerson',
                                     {'objectClass': 'iNetOrgPerson', 'sn': 'test-ldif', test_name_attr: 'test-add-operation'})

    def tearDown(self):
        self.connection.delete()
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testSingleSearchResultToLDIF(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(' + test_name_attr + '=test-ldif)', attributes = [test_name_attr, 'givenName', 'jpegPhoto'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

    def testMultipleSearchResultToLDIF(self):
        result = self.connection.search(searchBase = test_base, searchFilter = '(sn=t*)', attributes = [test_name_attr, 'givenName', 'sn'])
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

        self.assertGreater(len(self.connection.response), 8)

    def testAddRequestToLDIF(self):
        result = self.connection.add(testDnBuilder(test_base, 'test-add-operation'), 'iNetOrgPerson', {'objectClass': 'iNetOrgPerson', 'sn': 'test-add', test_name_attr: 'test-add-operation'})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'entryAlreadyExists'])
