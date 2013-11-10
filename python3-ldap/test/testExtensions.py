"""
Created on 2013.08.05

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
from ldap3.tls import Tls


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                     authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testGetReplicaListExtension(self):
        result = self.connection.extended('2.16.840.1.113719.1.27.100.19', 'cn=server')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'noSuchObject'])

    def testWhoAmIExtension(self):
        result = self.connection.extended('1.3.6.1.4.1.4203.1.11.3')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success', 'protocolError'])

    def testGetBindDNExtension(self):
        result = self.connection.extended('2.16.840.1.113719.1.27.100.31')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success'])

    def testStartTLSExtension(self):
        self.connection.server.tls = Tls()
        result = self.connection.extended('1.3.6.1.4.1.1466.20037')
        if not isinstance(result, bool):
            self.connection.getResponse(result)
        self.assertIn(self.connection.result['description'], ['success'])
