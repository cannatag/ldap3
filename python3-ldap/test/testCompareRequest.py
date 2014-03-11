"""
Created on 2013.05.23

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

from ldap3.protocol.rfc4511 import LDAPDN, AddRequest, AttributeList, Attribute, AttributeDescription, AttributeValue, CompareRequest, AttributeValueAssertion, AssertionValue, ValsAtLeast1
from ldap3.connection import Connection
from ldap3.server import Server
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_dn_builder, test_base


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(test_server, test_port, allowed_referral_hosts=('*', True))
        self.connection = Connection(server, auto_bind=True, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)

    def tearDown(self):
        self.connection.unbind()

    def test_compare(self):
        attribute1 = Attribute()
        vals1 = ValsAtLeast1()
        vals1[0] = AttributeValue('tost')
        attribute1['type'] = AttributeDescription('sn')
        attribute1['vals'] = vals1

        attribute2 = Attribute()
        vals2 = ValsAtLeast1()
        vals2[0] = AttributeValue('tust')
        attribute2['type'] = AttributeDescription('givenName')
        attribute2['vals'] = vals2

        attribute3 = Attribute()
        vals3 = ValsAtLeast1()
        vals3[0] = AttributeValue('inetOrgPerson')
        attribute3['type'] = AttributeDescription('objectClass')
        attribute3['vals'] = vals3

        attributes = AttributeList()
        attributes[0] = attribute1
        attributes[1] = attribute2
        attributes[2] = attribute3

        add_req = AddRequest()
        add_req['entry'] = LDAPDN(test_dn_builder(test_base, 'test-compare'))
        add_req['attributes'] = attributes

        self.connection.send('addRequest', add_req)

        ava = AttributeValueAssertion()
        ava['attributeDesc'] = AttributeDescription('givenName')
        ava['assertionValue'] = AssertionValue('tust')
        compare_req = CompareRequest()
        compare_req['entry'] = LDAPDN(test_dn_builder(test_base, 'test-compare'))
        compare_req['ava'] = ava

        self.connection.send('compareRequest', compare_req)
        self.assertTrue(True)
