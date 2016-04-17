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

    def test_add_member_to_group(self):
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-1'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-1'))
            self.connection.extend.novell.add_members_to_groups(self.delete_at_teardown[0][0],
                                                                self.delete_at_teardown[1][0],
                                                                check=False,
                                                                transaction=False)
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', attributes=['securityEquals', 'groupMembership'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response, result = self.connection.response, self.connection.result

            if response:
                self.assertTrue(self.delete_at_teardown[1][0] in (response[0]['attributes']['securityEquals'] if 'securityEquals' in response[0]['attributes'] else []))
                self.assertTrue(self.delete_at_teardown[1][0] in (response[0]['attributes']['groupMembership'] if 'groupMembership' in response[0]['attributes'] else []))
            else:
                self.assertFalse(True, self.delete_at_teardown[1][0] + ' not found')

            result = self.connection.search(self.delete_at_teardown[1][0], '(objectclass=*)', attributes=['member', 'equivalentToMe'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response, result = self.connection.response, self.connection.result

            if response:
                self.assertTrue(self.delete_at_teardown[0][0] in (response[0]['attributes']['member'] if 'member' in response[0]['attributes'] else []))
                self.assertTrue(self.delete_at_teardown[0][0] in (response[0]['attributes']['equivalentToMe'] if 'equivalentToMe' in response[0]['attributes'] else []))
            else:
                self.assertFalse(True, self.delete_at_teardown[0][0] + ' not found')

    def test_add_members_to_groups(self):
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-2'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-3'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-4'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-2', self.delete_at_teardown))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-3'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-4'))
            self.connection.extend.novell.add_members_to_groups([self.delete_at_teardown[0][0],
                                                                 self.delete_at_teardown[1][0],
                                                                 self.delete_at_teardown[2][0]],
                                                                [self.delete_at_teardown[3][0],
                                                                 self.delete_at_teardown[4][0],
                                                                 self.delete_at_teardown[5][0]],
                                                                check=True,
                                                                transaction=False
                                                                )
            for i in range(0, 2):
                result = self.connection.search(self.delete_at_teardown[i][0], '(objectclass=*)', attributes=['securityEquals', 'groupMembership'])
                if not self.connection.strategy.sync:
                    response, result = self.connection.get_response(result)
                else:
                    response, result = self.connection.response, self.connection.result

                if response:
                    for j in range(3, 5):
                        self.assertTrue(self.delete_at_teardown[j][0] in (response[0]['attributes']['securityEquals'] if 'securityEquals' in response[0]['attributes'] else []))
                        self.assertTrue(self.delete_at_teardown[j][0] in (response[0]['attributes']['groupMembership'] if 'groupMembership' in response[0]['attributes'] else []))
                else:
                    self.assertFalse(True, self.delete_at_teardown[i][0] + ' not found')

            for j in range(3, 5):
                result = self.connection.search(self.delete_at_teardown[j][0], '(objectclass=*)', attributes=['member', 'equivalentToMe'])
                if not self.connection.strategy.sync:
                    response, result = self.connection.get_response(result)
                else:
                    response, result = self.connection.response, self.connection.result

                if response:
                    for i in range(0, 2):
                        self.assertTrue(self.delete_at_teardown[i][0] in (response[0]['attributes']['member'] if 'member' in response[0]['attributes'] else []))
                        self.assertTrue(self.delete_at_teardown[i][0] in (response[0]['attributes']['equivalentToMe'] if 'equivalentToMe' in response[0]['attributes'] else []))
                else:
                    self.assertFalse(True, self.delete_at_teardown[j][0] + ' not found')

    def test_add_member_to_group_transactional(self):
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-5'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-5', self.delete_at_teardown))
            self.connection.extend.novell.add_members_to_groups(self.delete_at_teardown[0][0],
                                                                self.delete_at_teardown[1][0],
                                                                check=True,
                                                                transaction=True)
            result = self.connection.search(self.delete_at_teardown[0][0], '(objectclass=*)', attributes=['securityEquals', 'groupMembership'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response, result = self.connection.response, self.connection.result

            if response:
                self.assertTrue(self.delete_at_teardown[1][0] in (response[0]['attributes']['securityEquals'] if 'securityEquals' in response[0]['attributes'] else []))
                self.assertTrue(self.delete_at_teardown[1][0] in (response[0]['attributes']['groupMembership'] if 'groupMembership' in response[0]['attributes'] else []))
            else:
                self.assertFalse(True, self.delete_at_teardown[1][0] + ' not found')

        result = self.connection.search(self.delete_at_teardown[1][0], '(objectclass=*)', attributes=['member', 'equivalentToMe'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
        else:
            response, result = self.connection.response, self.connection.result

        if response:
            self.assertTrue(self.delete_at_teardown[0][0] in (response[0]['attributes']['member'] if 'member' in response[0]['attributes'] else []))
            self.assertTrue(self.delete_at_teardown[0][0] in (response[0]['attributes']['equivalentToMe'] if 'equivalentToMe' in response[0]['attributes'] else []))
        else:
            self.assertFalse(True, self.delete_at_teardown[0][0] + ' not found')

    def test_add_members_to_groups_transactional(self):
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-6'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-7'))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'user-8'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-6', self.delete_at_teardown))  # this group has members but other attributes are not set
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-7'))
            self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'group-8'))
            self.connection.extend.novell.add_members_to_groups([self.delete_at_teardown[0][0],
                                                                 self.delete_at_teardown[1][0],
                                                                 self.delete_at_teardown[2][0]],
                                                                [self.delete_at_teardown[3][0],
                                                                 self.delete_at_teardown[4][0],
                                                                 self.delete_at_teardown[5][0]],
                                                                check=True,
                                                                transaction=True
                                                                )
            for i in range(0, 2):
                result = self.connection.search(self.delete_at_teardown[i][0], '(objectclass=*)', attributes=['securityEquals', 'groupMembership'])
                if not self.connection.strategy.sync:
                    response, result = self.connection.get_response(result)
                else:
                    response, result = self.connection.response, self.connection.result

                if response:
                    for j in range(3, 5):
                        self.assertTrue(self.delete_at_teardown[j][0] in (response[0]['attributes']['securityEquals'] if 'securityEquals' in response[0]['attributes'] else []))
                        self.assertTrue(self.delete_at_teardown[j][0] in (response[0]['attributes']['groupMembership'] if 'groupMembership' in response[0]['attributes'] else []))
                else:
                    self.assertFalse(True, self.delete_at_teardown[i][0] + ' not found')

            for j in range(3, 5):
                result = self.connection.search(self.delete_at_teardown[j][0], '(objectclass=*)', attributes=['member', 'equivalentToMe'])
                if not self.connection.strategy.sync:
                    response, result = self.connection.get_response(result)
                else:
                    response, result = self.connection.response, self.connection.result

                if response:
                    for i in range(0, 2):
                        self.assertTrue(self.delete_at_teardown[i][0] in (response[0]['attributes']['member'] if 'member' in response[0]['attributes'] else []))
                        self.assertTrue(self.delete_at_teardown[i][0] in (response[0]['attributes']['equivalentToMe'] if 'equivalentToMe' in response[0]['attributes'] else []))
                else:
                    self.assertFalse(True, self.delete_at_teardown[j][0] + ' not found')
