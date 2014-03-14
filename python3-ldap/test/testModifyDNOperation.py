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

from ldap3.core.server import Server
from ldap3.core.connection import Connection
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, test_dn_builder, test_moved, test_name_attr


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True))
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication)

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def test_modify_dn_operation(self):
        result = self.connection.delete(test_dn_builder(test_base, 'test-add-modified-dn'))
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'noSuchObject'])

        result = self.connection.delete(test_dn_builder(test_base, 'test-add-for-modify-dn'))
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'noSuchObject'])

        result = self.connection.add(test_dn_builder(test_base, 'test-add-for-modify-dn'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-compare', 'givenName': 'modify-dn'})
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'entryAlreadyExists'])

        result = self.connection.modify_dn(test_dn_builder(test_base, 'test-add-for-modify-dn'), test_name_attr + '=test-add-modified-dn')
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'noSuchObject'])

    def test_move_dn(self):
        result = self.connection.delete(test_dn_builder(test_base, 'test-add-for-move-dn'))
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'noSuchObject'])

        result = self.connection.add(test_dn_builder(test_base, 'test-add-for-move-dn'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-compare', 'givenName': 'move-dn'})
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'entryAlreadyExists'])

        result = self.connection.delete(test_dn_builder(test_moved, 'test-add-for-move-dn'))
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['success', 'noSuchObject', 'busy'])

        result = self.connection.modify_dn(test_dn_builder(test_base, 'test-add-for-move-dn'), test_name_attr + '=test-add-for-move-dn', new_superior=test_moved)
        if not isinstance(result, bool):
            self.connection.get_response(result)
        self.assertTrue(self.connection.result['description'] in ['other', 'success', 'entryAlreadyExists', 'noSuchObject'])
