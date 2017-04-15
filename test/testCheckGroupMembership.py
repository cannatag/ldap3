"""
"""

# Created on 2016.05.14
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

from test.config import add_user, add_group, get_connection, drop_connection, random_id, test_server_type

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

    def test_check_group_membership(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-2'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-2'))
            self.connection.extend.novell.add_members_to_groups(self.delete_at_teardown[0][0],
                                                                self.delete_at_teardown[1][0],
                                                                fix=True,
                                                                transaction=True)

            # valid user in valid group
            result = self.connection.extend.novell.check_groups_memberships(self.delete_at_teardown[0][0], self.delete_at_teardown[1][0])
            self.assertTrue(result)

            # invalid user in valid group
            result = self.connection.extend.novell.check_groups_memberships(self.delete_at_teardown[3][0], self.delete_at_teardown[1][0])
            self.assertFalse(result)

            # invalid user in invalid group
            result = self.connection.extend.novell.check_groups_memberships(self.delete_at_teardown[0][0], self.delete_at_teardown[2][0])
            self.assertFalse(result)

    def test_check_groups_membership(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-2'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-3'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-2'))
            self.connection.extend.novell.add_members_to_groups(self.delete_at_teardown[0][0],
                                                                (self.delete_at_teardown[1][0], self.delete_at_teardown[2][0]),
                                                                fix=True,
                                                                transaction=True)

            # valid user in valid groups
            result = self.connection.extend.novell.check_groups_memberships(self.delete_at_teardown[0][0], (self.delete_at_teardown[1][0], self.delete_at_teardown[2][0]))
            self.assertTrue(result)

            # invalid user in valid groups
            result = self.connection.extend.novell.check_groups_memberships(self.delete_at_teardown[4][0], (self.delete_at_teardown[1][0], self.delete_at_teardown[2][0]))
            self.assertFalse(result)

            # invalid user in invalid groups
            result = self.connection.extend.novell.check_groups_memberships(self.delete_at_teardown[0][0], (self.delete_at_teardown[1][0], self.delete_at_teardown[3][0]))
            self.assertFalse(result)


    def test_check_group_memberships(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-2'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-3'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-2'))
            self.connection.extend.novell.add_members_to_groups((self.delete_at_teardown[0][0], self.delete_at_teardown[1][0]),
                                                                self.delete_at_teardown[2][0],
                                                                fix=True,
                                                                transaction=True)

            # valid users in valid group
            result = self.connection.extend.novell.check_groups_memberships((self.delete_at_teardown[0][0], self.delete_at_teardown[1][0]), self.delete_at_teardown[2][0])
            self.assertTrue(result)

            # invalid users in valid group
            result = self.connection.extend.novell.check_groups_memberships((self.delete_at_teardown[0][0], self.delete_at_teardown[3][0]), self.delete_at_teardown[2][0])
            self.assertFalse(result)

            # invalid users in invalid group
            result = self.connection.extend.novell.check_groups_memberships((self.delete_at_teardown[0][0], self.delete_at_teardown[3][0]), self.delete_at_teardown[4][0])
            self.assertFalse(result)


    def test_check_groups_memberships(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-2'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-2'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-3'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-3'))
            self.connection.extend.novell.add_members_to_groups((self.delete_at_teardown[0][0], self.delete_at_teardown[1][0]),
                                                                self.delete_at_teardown[2][0],
                                                                fix=True,
                                                                transaction=True)

            self.connection.extend.novell.add_members_to_groups((self.delete_at_teardown[0][0], self.delete_at_teardown[1][0]),
                                                                self.delete_at_teardown[3][0],
                                                                fix=True,
                                                                transaction=True)

            # valid users in valid groups
            result = self.connection.extend.novell.check_groups_memberships((self.delete_at_teardown[0][0], self.delete_at_teardown[1][0]), (self.delete_at_teardown[2][0],self.delete_at_teardown[3][0]))
            self.assertTrue(result)

            # invalid users in valid groups
            result = self.connection.extend.novell.check_groups_memberships((self.delete_at_teardown[0][0], self.delete_at_teardown[3][0]), (self.delete_at_teardown[2][0],self.delete_at_teardown[3][0]))
            self.assertFalse(result)

            # invalid users in invalid groups
            result = self.connection.extend.novell.check_groups_memberships((self.delete_at_teardown[0][0], self.delete_at_teardown[4][0]), (self.delete_at_teardown[2][0], self.delete_at_teardown[5][0]))
            self.assertFalse(result)
