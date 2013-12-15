# -*- coding: utf-8 -*-
"""
Created on 2013.12.13

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
from ldap3 import STRATEGY_LDIF_PRODUCER
from ldap3.server import Server
from ldap3.connection import Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, testDnBuilder, test_name_attr


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = STRATEGY_LDIF_PRODUCER, user = test_user, password = test_password,
                                     authentication = test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testAddRequestToLDIF(self):
        controls = list()
        controls.append(('2.16.840.1.113719.1.27.103.7', True, 'givenName'))
        controls.append(('2.16.840.1.113719.1.27.103.7', False, 'sn'))
        controls.append(('2.16.840.1.113719.1.27.103.7', False, u'à'))
        controls.append(('2.16.840.1.113719.1.27.103.7', False, 'trailingspace '))
        self.connection.add(testDnBuilder(test_base, 'test-add-operation'), 'iNetOrgPerson', {'objectClass': 'iNetOrgPerson', 'sn': 'test-add', test_name_attr: 'test-add-operation'}, controls = controls)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-add-operation,o=test' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 true: givenName' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 false: sn' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 false:: w6DDoA==' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 false:: dHJhaWxpbmdzcGFjZSA=' in response)
        self.assertTrue('changetype: add' in response)
        self.assertTrue('objectClass: inetorgperson' in response)
        self.assertTrue('sn: test-add' in response)
        self.assertTrue('cn: test-add-operation' in response)
