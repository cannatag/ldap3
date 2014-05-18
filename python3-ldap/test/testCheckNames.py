"""
Created on 2014.05.01

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
from ldap3 import STRATEGY_REUSABLE_THREADED, GET_ALL_INFO
from ldap3.core.exceptions import  LDAPException

from ldap3 import Server, Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, test_dn_builder, test_lazy_connection, test_name_attr


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=GET_ALL_INFO)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=True)

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_wrong_assertion(self):
        ok = False
        try:
            result = self.connection.search(search_base=test_base, search_filter='(xxx=yyy)', attributes=[test_name_attr])
        except LDAPException:
            ok = True

        self.assertTrue(ok)

    def test_wrong_attribute(self):
        ok = False
        try:
            result = self.connection.search(search_base=test_base, search_filter='(cn=yyy)', attributes=[test_name_attr, 'xxx'])
        except LDAPException:
            ok = True

        self.assertTrue(ok)

    def test_wrong_object_class_add(self):
        ok = False
        try:
            result = self.connection.add(test_dn_builder(test_base, 'test-add-operation-wrong'), 'iNetOrgPerson', {'objectClass': ['iNetOrgPerson', 'xxx'], 'sn': 'test-add', test_name_attr: 'test-add-operation'})
        except LDAPException:
            ok = True
        self.assertTrue(ok)

    def test_valid_assertion(self):
        result = self.connection.search(search_base=test_base, search_filter='(cn=test*)', attributes=[test_name_attr])
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(len(response) > 1)

    def test_valid_attribute(self):
        result = self.connection.search(search_base=test_base, search_filter='(cn=test*)', attributes=[test_name_attr, 'givenName'])
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(len(response) > 1)

    def test_valid_object_class_add(self):
        result = self.connection.add(test_dn_builder(test_base, 'test-add-operation-check-names'), 'iNetOrgPerson', {'objectClass': ['iNetOrgPerson', 'Person'], 'sn': 'test-add', test_name_attr: 'test-add-operation-check-names'})
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'entryAlreadyExists'])
