# """
# Created on 2016.04.16
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

from test import test_base, add_user, add_group, get_connection, drop_connection, random_id, test_server_type

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_add_members_to_groups_transactional(self):
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-2'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-3'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-2'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-3'))
            self.connection.extend.novell.add_members_to_groups([self.delete_at_teardown[0][0],
                                                                 self.delete_at_teardown[1][0],
                                                                 self.delete_at_teardown[2][0]],
                                                                [self.delete_at_teardown[3][0],
                                                                 self.delete_at_teardown[4][0],
                                                                 self.delete_at_teardown[5][0]]
                                                                )


def test_add_member_to_group_transactional(self):
    if test_server_type == 'EDIR':
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
        self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
        self.connection.extend.novell.add_members_to_groups(self.delete_at_teardown[0][0], self.delete_at_teardown[3][0])
