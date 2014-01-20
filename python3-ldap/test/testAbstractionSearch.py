"""
Created on 2014.01.19

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

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

from pprint import pprint
import unittest
from ldap3.abstraction.defs import ObjectDef, AttrDef
from ldap3.abstraction.reader import Reader, _createQueryDict
from ldap3 import Server, Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, testDnBuilder, test_name_attr
from ldap3 import SEARCH_SCOPE_WHOLE_SUBTREE


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                     authentication = test_authentication)
        self.connection.add(testDnBuilder(test_base, 'test-search-(parentheses)'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-search-(parentheses)'})

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testSearchFilterWithObjectClass(self):
        o = ObjectDef('inetOrgPerson')
        o + AttrDef('cn', 'Common Name')
        o + AttrDef('sn', 'Surname')
        o + AttrDef('givenName', 'Given Name')

        queryText = 'Common Name:=test*'
        r = Reader(self.connection, o, queryText, 'o=test')

        results = r.search()
        print(results)
        self.assertEqual(len(results), 127)
