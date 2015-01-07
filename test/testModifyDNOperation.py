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

from test import test_base, test_moved, test_name_attr, random_id, \
    get_connection, add_user, drop_connection


testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_modify_dn_operation(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'modify-dn-1'))
        result = self.connection.modify_dn(self.delete_at_teardown[0][0], test_name_attr + '=' + testcase_id + 'modified-dn-1')
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
        self.delete_at_teardown[0] = (self.delete_at_teardown[0][0].replace('modify-dn-1', 'modified-dn-1'), self.delete_at_teardown[0][1])

    def test_move_dn(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'modify-dn-2'))
        done = False
        counter = 20
        while not done:  # tries move operation for at maximum 20 times - partition may be busy while moving (at least on eDirectory)
            result = self.connection.modify_dn(self.delete_at_teardown[0][0], test_name_attr + '=' + testcase_id + 'modify-dn-2', new_superior=test_moved)
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            if result['description'] == 'other' and counter > 0:
                counter -= 1
                print(result)
                if counter > 0:
                    continue
            done = True
        self.assertEqual(result['description'], 'success')
        self.delete_at_teardown[0] = (self.delete_at_teardown[0][0].replace(test_base, test_moved), self.delete_at_teardown[0][1])
