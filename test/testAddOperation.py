"""
"""

# Created on 2013.06.06
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2018 Giovanni Cannata
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
from copy import deepcopy

from test.config import get_connection, drop_connection, add_user, random_id, get_add_user_attributes,\
    test_user_password, generate_dn, test_base


testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_add(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'add-operation-1'))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])

    def test_add_bytes(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'add-operation-2', test_bytes=True))
        self.assertEqual('success', self.delete_at_teardown[0][1]['description'])

    def test_unmodified_attributes_dict(self):
        attributes = get_add_user_attributes(testcase_id, 'add-operation-3', test_user_password)
        object_class = attributes.pop('objectClass')
        copy_of_attributes = deepcopy(attributes)
        dn = generate_dn(test_base, testcase_id, 'add-operation-3')
        self.connection.add(dn, object_class, attributes)
        self.connection.delete(dn)
        self.assertDictEqual(copy_of_attributes, attributes)
