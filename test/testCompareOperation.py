"""
"""

# Created on 2013.06.06
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

from test import random_id, get_connection, drop_connection, add_user


testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(check_names=True)
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'compare-1', attributes={'givenName': 'compare'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_compare_true(self):
        result = self.connection.compare(self.delete_at_teardown[0][0], 'givenName', 'compare')
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result

        self.assertEqual(result['description'], 'compareTrue')

    def test_compare_false(self):
        result = self.connection.compare(self.delete_at_teardown[0][0], 'givenName', 'error')
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result

        self.assertEqual(result['description'], 'compareFalse')
