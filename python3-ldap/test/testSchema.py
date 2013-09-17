"""
Created on 2013.09.13

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
from ldap3 import GET_ALL_INFO
from ldap3.protocol.schema import SchemaInfo, ObjectClassInfo, AttributeTypeInfo
from ldap3.server import Server
from ldap3.connection import Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy

class Test(unittest.TestCase):
    def setUp(self):
        self.server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True), getInfo = GET_ALL_INFO)
        self.connection = Connection(self.server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                     authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testSchema(self):
        self.assertIsInstance(self.server.schema, SchemaInfo)

    def testObjectClasses(self):
        self.assertIsInstance(self.server.schema.objectClasses['2.5.6.6'], ObjectClassInfo)
        print(self.server.schema.objectClasses)

    def testAttributesTypes(self):
        self.assertIsInstance(self.server.schema.attributeTypes['2.5.4.3'], AttributeTypeInfo)
