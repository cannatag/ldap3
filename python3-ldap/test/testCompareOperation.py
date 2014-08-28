# Created on 2013.06.06
#
# @author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
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
from ldap3 import Server, Connection, STRATEGY_REUSABLE_THREADED, GET_ALL_INFO
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, test_base, dn_for_test, test_lazy_connection, test_check_names, test_get_info


class Test(unittest.TestCase):
    def setUp(self):
        server = Server(host=test_server, port=test_port, allowed_referral_hosts=('*', True), get_info=test_get_info)
        self.connection = Connection(server, auto_bind=True, version=3, client_strategy=test_strategy, user=test_user, password=test_password, authentication=test_authentication, lazy=test_lazy_connection, pool_name='pool1', check_names=test_check_names)
        result = self.connection.add(dn_for_test(test_base, 'test-add-for-compare'), None, {'objectClass': 'iNetOrgPerson', 'sn': 'test-compare', 'givenName': 'compare'})
        if not isinstance(result, bool):
            self.connection.get_response(result)

    def tearDown(self):
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertFalse(self.connection.bound)

    def test_compare_true(self):
        result = self.connection.compare(dn_for_test(test_base, 'test-add-for-compare'), 'givenName', 'compare')
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result

        self.assertEqual(result['description'], 'compareTrue')

    def test_compare_false(self):
        result = self.connection.compare(dn_for_test(test_base, 'test-add-for-compare'), 'givenName', 'error')
        if not isinstance(result, bool):
            response, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result

        self.assertEqual(result['description'], 'compareFalse')
