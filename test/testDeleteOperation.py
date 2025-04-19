"""
"""

# Created on 2013.06.06
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2025 Giovanni Cannata
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

from test.config import random_id, get_connection, drop_connection, add_user

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection(check_names=True)
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'delete-1'))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_delete(self):
        result = self.connection.delete(self.delete_at_teardown[0][0])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.delete_at_teardown = []  # remove object from delete list if delete is successful

    def test_delete_with_get_request(self):
        result = self.connection.delete(self.delete_at_teardown[0][0])
        if not self.connection.strategy.sync:
            response, result, request = self.connection.get_response(result, get_request=True)
            self.assertEqual(request['type'], 'delRequest')
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.delete_at_teardown = []  # remove object from delete list if delete is successful
