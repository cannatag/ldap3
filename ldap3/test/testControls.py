# Created on 2013.07.31
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
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy, \
    test_base, test_lazy_connection, test_get_info, test_server_mode, test_pooling_strategy, test_pooling_active, test_pooling_exhaust, \
    random_id, get_connection, drop_connection, add_user

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'controls-1', attributes={'givenName': 'given name-1'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'controls-2', attributes={'givenName': 'given name-2'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'controls-3', attributes={'givenName': 'given name-3'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_with_controls(self):
        controls = list()
        controls.append(('2.16.840.1.113719.1.27.103.7', True, 'givenName'))  # grouping [Novell]
        result = self.connection.search(test_base, '(cn=' + testcase_id + 'controls-*)', attributes=['sn', 'givenName'], size_limit=0, controls=controls)
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            response = self.connection.response
            result = self.connection.result

        self.assertTrue(result['description'] in ['success', 'operationsError'])
