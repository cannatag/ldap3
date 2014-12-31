# Created on 2014.02.02
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
from ldap3 import Server, Connection, ServerPool, STRATEGY_REUSABLE_THREADED, ServerPool
from test import test_server, test_port, test_user, test_password, test_authentication, test_strategy,\
    test_lazy_connection, test_get_info, test_server_mode, test_pooling_strategy, test_pooling_active, test_pooling_exhaust, \
    get_connection, drop_connection


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()

    def tearDown(self):
        drop_connection(self.connection)
        self.assertFalse(self.connection.bound)

    def test_open_connection(self):
        self.connection.open()
        self.assertEqual(self.connection.closed, False)
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertEqual(self.connection.closed, True)
        self.assertEqual(self.connection.bound, False)

    def test_bind_connection(self):
        self.connection.open()
        self.assertEqual(self.connection.closed, False)
        self.connection.bind()
        self.assertEqual(self.connection.bound, True)
        self.connection.unbind()
        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()
        self.assertEqual(self.connection.closed, True)
        self.assertEqual(self.connection.bound, False)

    def test_connection_in_context(self):
        with self.connection:
            self.assertEqual(self.connection.closed, False)
            self.assertEqual(self.connection.bound, True)

        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()

        self.assertEqual(self.connection.closed, False)
        self.assertEqual(self.connection.bound, True)

    def test_connection_in_context_with_as(self):
        with self.connection as c:
            self.assertEqual(c.closed, False)
            self.assertEqual(c.bound, True)

        if self.connection.strategy_type == STRATEGY_REUSABLE_THREADED:
            self.connection.strategy.terminate()

        self.assertEqual(self.connection.closed, False)
        self.assertEqual(self.connection.bound, True)
