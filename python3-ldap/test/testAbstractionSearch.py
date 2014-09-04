# Created on 2014.01.19
#
# @author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest

from ldap3.abstract import ObjectDef, AttrDef, Reader
from ldap3 import Server, Connection, STRATEGY_REUSABLE_THREADED, GET_ALL_INFO
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, dn_for_test, test_lazy_connection, test_get_info, test_check_names


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=test_check_names)
        result = self.connection.add(dn_for_test(test_base, 'test-group'), [], {'objectClass': 'groupOfNames', 'member': ['cn=test-add,o=test', 'cn=test-compare,o=test', 'cn=test-modify,o=test', 'cn=test-modify-dn,o=test']})
        if not isinstance(result, bool):
            self.connection.get_response(result)

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_search_filter_with_object_class(self):
        reverse = lambda a, e: e[::-1]
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name', post_query=reverse)

        query_text = 'Common Name:=test-search*'
        r = Reader(self.connection, o, query_text, 'o=test')

        results = r.search()
        self.assertEqual(len(results), 7)

    def test_search_with_dereference(self):
        reverse = lambda a, e: e[::-1]

        def raise_parentheses_rank(_, l):
            up = {'(': '[', ')': ']', '[': '{', ']': '}', '{': '<', '}': '>'}
            r = []
            for e in l:
                s = ''
                for c in e:
                    s += up[c] if c in up else c
                r.append(s)

            return r

        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'Common Name', post_query=reverse)
        ou += AttrDef('sn', 'Surname')
        ou += AttrDef('givenName', 'Given Name', post_query=raise_parentheses_rank)
        ou += AttrDef('ACL')
        qu = 'Common Name: test-search*'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        self.assertEqual(len(lu), 7)

        og = ObjectDef('groupOfNames')
        og += AttrDef('member', dereference_dn=ou)
        og += 'cn'
        qg = 'cn := test-group'
        rg = Reader(self.connection, og, qg, test_base)
        lg = rg.search()
        self.assertEqual(len(lg), 1)

        eg = lg[0]
        mg = eg.member
        self.assertEqual(len(mg), 4)
        ug = eg.member[0]
        self.assertEqual(str(ug.surname), 'tost')

    def test_search_with_pre_query(self):
        change = lambda attr, value: 'test-search*'

        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'Common Name', pre_query=change)
        ou += AttrDef('sn', 'Surname')
        ou += AttrDef('givenName', 'Given Name')
        ou += AttrDef('ACL')
        qu = 'Common Name := bug'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        self.assertEqual(len(lu), 7)

    def test_search_with_default(self):
        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'CommonName')
        ou += AttrDef('employeeType', key='Employee', default='not employed')
        qu = 'CommonName := test-add*'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        self.assertEqual(str(lu[0].employee), 'not employed')

    def test_refresh_entry(self):  # require manual modification of attribute value
        ou = ObjectDef('iNetOrgPerson')
        ou += AttrDef('cn', 'CommonName')
        ou += AttrDef('sn', 'Surname')
        qu = 'CommonName := test-add*'
        ru = Reader(self.connection, ou, qu, test_base)
        lu = ru.search()
        eu = lu[0]
        eu.refresh()
        self.assertEqual(str(eu.surname), 'tost')
