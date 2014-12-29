# Created on 2013.06.06
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of ldap3.
#
# ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest
from ldap3 import Server, Connection, ServerPool, STRATEGY_REUSABLE_THREADED
from test import test_server, test_port, test_user, test_password, test_authentication, \
    test_strategy, test_base, generate_dn, test_moved, test_name_attr, test_lazy_connection, \
    test_get_info, test_server_mode, test_pooling_strategy, test_pooling_active, test_pooling_exhaust


class Test(unittest.TestCase):
    def setUp(self):
        if isinstance(test_server, (list, tuple)):
            server = ServerPool(pool_strategy=test_pooling_strategy, active=test_pooling_active, exhaust=test_pooling_exhaust)
            for host in test_server:
                server.add(Server(host=host, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode))
        else:
            server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info, mode=test_server_mode)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1')

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_modify_dn_operation(self):
        result = self.connection.delete(generate_dn(test_base, 'test-add-modified-dn'))
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'noSuchObject'])

        result = self.connection.delete(generate_dn(test_base, 'test-add-for-modify-dn'))
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'noSuchObject'])

        result = self.connection.add(generate_dn(test_base, 'test-add-for-modify-dn'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-compare', 'givenName': 'modify-dn'})
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'entryAlreadyExists'])

        result = self.connection.modify_dn(generate_dn(test_base, 'test-add-for-modify-dn'), test_name_attr + '=test-add-modified-dn')
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        print(result['description'])
        self.assertTrue(result['description'] in ['success', 'noSuchObject'])

    def test_move_dn(self):
        result = self.connection.delete(generate_dn(test_base, 'test-add-for-move-dn'))
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'noSuchObject'])

        result = self.connection.add(generate_dn(test_base, 'test-add-for-move-dn'), [], {'objectClass': 'iNetOrgPerson', 'sn': 'test-add-for-move-dn', 'givenName': 'move-dn'})
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'entryAlreadyExists'])

        result = self.connection.delete(generate_dn(test_moved, 'test-add-for-move-dn'))
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['success', 'noSuchObject', 'busy'])

        result = self.connection.modify_dn(generate_dn(test_base, 'test-add-for-move-dn'), test_name_attr + '=test-add-for-move-dn', new_superior=test_moved)
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result
        self.assertTrue(result['description'] in ['other', 'success', 'entryAlreadyExists', 'noSuchObject'])
