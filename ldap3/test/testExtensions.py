# """
# Created on 2013.08.05
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

from ldap3 import Tls
from test import test_server_context, random_id, get_connection, drop_connection, \
    test_server_edir_name, test_server_type

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()

    def tearDown(self):
        drop_connection(self.connection)
        self.assertFalse(self.connection.bound)

    def test_get_replica_list_extension(self):
        result = self.connection.extended('2.16.840.1.113719.1.27.100.19', ('cn=' + test_server_edir_name + ',' + test_server_context))

        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_who_am_i_extension(self):
        if not test_server_type == 'EDIR':
            result = self.connection.extended('1.3.6.1.4.1.4203.1.11.3')
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')

    def test_get_bind_dn_extension(self):
        result = self.connection.extended('2.16.840.1.113719.1.27.100.31')
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_start_tls_extension(self):
        self.connection.server.tls = Tls()
        result = self.connection.extended('1.3.6.1.4.1.1466.20037')
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
