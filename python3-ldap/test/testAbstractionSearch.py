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
import unittest
from ldap3.abstraction import ObjectDef, AttrDef, Reader
from ldap3 import Server, Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, testDnBuilder


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host = test_server, port = test_port, allowedReferralHosts = ('*', True))
        self.connection = Connection(server, autoBind = True, version = 3, clientStrategy = test_strategy, user = test_user, password = test_password,
                                     authentication = test_authentication)
        self.connection.add(testDnBuilder(test_base, 'test-group'), [], {'objectClass': 'groupOfNames', 'member': ['cn=test-add,o=test', 'cn=test-compare,o=test', 'cn=test-delete,o=test', 'cn=test-modify,o=test', 'cn=test-modify-dn,o=test']})

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def testSearchFilterWithObjectClass(self):
        reverse = lambda a, e: e[::-1]
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name', postQuery = reverse)

        queryText = 'Common Name:=test-add*'
        r = Reader(self.connection, o, queryText, 'o=test')

        results = r.search()
        self.assertEqual(len(results), 6)

    def testSearchWithDereference(self):
        reverse = lambda a, e: e[::-1]

        def raiseParenthesesRank(a, l):
            up = {'(': '[', ')': ']', '[': '{', ']': '}', '{': '<', '}': '>'}
            r = []
            for e in l:
                s = ''
                for c in e:
                    s += up[c] if c in up else c
                r.append(s)

            return r

        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'Common Name', postQuery = reverse)
        ou += AttrDef('sn', 'Surname')
        ou += AttrDef('givenName', 'Given Name', postQuery = raiseParenthesesRank)
        ou += AttrDef('ACL')
        qu = 'Common Name: test-add*'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        self.assertEqual(len(lu), 6)

        og = ObjectDef('groupOfNames')
        og += AttrDef('member', dereferenceDN = ou)
        og += 'cn'
        qg = 'cn := test*'
        rg = Reader(self.connection, og, qg, test_base)
        lg = rg.search()
        self.assertEqual(len(lg), 1)

        eg = lg[0]
        mg = eg.member
        self.assertEqual(len(mg), 3)
        ug = eg.member[0]
        self.assertEqual(str(ug.surname), 'tost')

    def testSearchWithPreQuery(self):
        change = lambda attr, value: 'test-del*'

        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'Common Name', preQuery = change)
        ou += AttrDef('sn', 'Surname')
        ou += AttrDef('givenName', 'Given Name')
        ou += AttrDef('ACL')
        qu = 'Common Name := bug'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        self.assertEqual(len(lu), 1)

    def testSearchWithDefault(self):
        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'CommonName')
        ou += AttrDef('employeeType', key = 'Employee', default = 'not employed')
        qu = 'CommonName := test-add*'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        self.assertEqual(str(lu[0].employee), 'not employed')
