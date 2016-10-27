"""
"""

# Created on 2016.04.17
#
# Author: Giovanni Cannata
#
# Copyright 2016 Giovanni Cannata
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

from ldap3 import MODIFY_REPLACE
from ldap3.protocol.controls import build_control
from ldap3.protocol.novell import Integer
from test import add_user, get_connection, drop_connection, random_id, test_server_type

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_commit_transaction(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            transaction_control = self.connection.extend.novell.start_transaction()
            self.connection.modify(self.delete_at_teardown[0][0], {'givenName': (MODIFY_REPLACE, ['user-1b'])}, controls=[transaction_control])
            self.connection.modify(self.delete_at_teardown[0][0], {'sn': (MODIFY_REPLACE, ['sn-user-1b'])}, controls=[transaction_control])
            result = self.connection.extend.novell.end_transaction(commit=True, controls=[transaction_control])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', attributes=['givenName', 'sn'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response, result = self.connection.response, self.connection.result

            if response:
                self.assertEquals(response[0]['attributes']['givenName'][0], 'user-1b')
                self.assertEquals(response[0]['attributes']['sn'][0], 'sn-user-1b')
            else:
                self.assertFalse(True, self.delete_at_teardown[0][0] + ' not found')

    def test_abort_transaction(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            transaction_control = self.connection.extend.novell.start_transaction()
            self.connection.modify(self.delete_at_teardown[0][0], {'givenName': (MODIFY_REPLACE, ['user-1b'])}, controls=[transaction_control])
            self.connection.modify(self.delete_at_teardown[0][0], {'sn': (MODIFY_REPLACE, ['sn-user-1b'])}, controls=[transaction_control])
            result = self.connection.extend.novell.end_transaction(commit=False, controls=[transaction_control])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', attributes=['givenName', 'sn'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response, result = self.connection.response, self.connection.result

            if response:
                # self.assertEquals(response[0]['attributes']['givenName'][0], 'user-1b')
                self.assertEquals(response[0]['attributes']['sn'][0], 'user-1')
            else:
                self.assertFalse(True, self.delete_at_teardown[0][0] + ' not found')

    def test_invalid_transaction_cookie(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            transaction_control = self.connection.extend.novell.start_transaction()
            invalid_transaction_control = build_control('2.16.840.1.113719.1.27.103.7', True, Integer(12345678), encode_control_value=True)
            self.connection.modify(self.delete_at_teardown[0][0], {'givenName': (MODIFY_REPLACE, ['user-1b'])}, controls=[transaction_control])
            self.connection.modify(self.delete_at_teardown[0][0], {'sn': (MODIFY_REPLACE, ['sn-user-1b'])}, controls=[invalid_transaction_control])
            result = self.connection.extend.novell.end_transaction(commit=True, controls=[transaction_control])
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', attributes=['givenName', 'sn'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response, result = self.connection.response, self.connection.result

            if response:
                self.assertEquals(response[0]['attributes']['givenName'][0], 'user-1b')
                self.assertEquals(response[0]['attributes']['sn'][0], 'user-1')
            else:
                self.assertFalse(True, self.delete_at_teardown[0][0] + ' not found')
