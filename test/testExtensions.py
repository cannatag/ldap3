"""
"""

# Created on 2013.08.05
#
# Author: Giovanni Cannata
#
# Copyright 2013, 2014, 2015, 2016 Giovanni Cannata
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
from test.config import test_server_context, random_id, get_connection, drop_connection, \
    test_server_edir_name, test_server_type

testcase_id = None


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()

    def tearDown(self):
        drop_connection(self.connection)
        self.assertFalse(self.connection.bound)

    def test_get_replica_list_extension(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.extended('2.16.840.1.113719.1.27.100.19', ('cn=' + test_server_edir_name + ',' + test_server_context))

            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')

    def test_who_am_i_extension(self):
        if not test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.extended('1.3.6.1.4.1.4203.1.11.3')
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')

    def test_get_bind_dn_extension(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.extended('2.16.840.1.113719.1.27.100.31')
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')

    def test_start_tls_extension(self):
        if not self.connection.strategy.no_real_dsa:
            connection = get_connection(use_ssl=False)
            connection.server.tls = Tls()
            result = connection.start_tls()
            self.assertTrue(result)
            connection.unbind()
