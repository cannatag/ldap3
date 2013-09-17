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


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password, authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testModifyDNOperation(self):
        result = self.connection.delete('cn=test-add-modified-dn,o=test')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchObject'])

        result = self.connection.delete('cn=test-add-for-modifyDN,o=test')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchObject'])

        result = self.connection.add('cn=test-add-for-modifyDN,o=test', [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-compare', 'givenName': 'modify-dn'})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'entryAlreadyExists'])

        result = self.connection.modifyDn('cn=test-add-for-modifyDN,o=test', 'cn=test-add-modified-dn')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchObject'])

    def testMoveDN(self):
        result = self.connection.delete('cn=test-add-for-move-dn,o=test')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchObject'])

        result = self.connection.add('cn=test-add-for-move-dn,o=test', [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-compare', 'givenName': 'move-dn'})
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'entryAlreadyExists'])

        result = self.connection.delete('cn=test-add-for-move-dn,ou=moved,o=test')
        if not isinstance(result, bool):
             self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchObject', 'busy'])

        result = self.connection.modifyDn('cn=test-add-for-move-dn,o=test', 'cn=test-add-for-move-dn', newSuperior = 'ou=moved,o=test')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['other', 'success', 'entryAlreadyExists', 'noSuchObject'])
