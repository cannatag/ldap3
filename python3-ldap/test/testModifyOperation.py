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
from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password, authentication = test_authentication)
        self.connection.add('cn=test-add-for-modify,o=test', [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-add-for-modify'})

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testModifyReplace(self):
        result = self.connection.modify('cn=test-add-for-modify,o=test', {'givenName': (MODIFY_REPLACE, ['test-modified-replace'])})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertEqual(self.connection.result['description'], 'success')

    def testModifyAdd(self):
        result = self.connection.modify('cn=test-add-for-modify,o=test', {'givenName': (MODIFY_ADD, ['test-modified-added'])})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'attributeOrValueExists'])

    def testModifyDeleted(self):
        result = self.connection.modify('cn=test-add-for-modify,o=test', {'givenName': (MODIFY_ADD, ['test-modified-added2'])})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'attributeOrValueExists'])

        result = self.connection.modify('cn=test-add-for-modify,o=test', {'givenName': (MODIFY_ADD, ['test-modified-added3'])})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['attributeOrValueExists', 'success'])

        result = self.connection.modify('cn=test-add-for-modify,o=test', {'givenName': (MODIFY_DELETE, ['test-modified-added2'])})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchAttribute'])
