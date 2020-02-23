"""
"""
# Created on 2014.01.19
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2018 Giovanni Cannata
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
from time import sleep

from ldap3 import Writer, Reader, AttrDef, ObjectDef
from ldap3.core.exceptions import LDAPCursorError
from test.config import test_base, get_connection, drop_connection, random_id, test_moved, add_user, test_multivalued_attribute, test_server_type
from ldap3.abstract import STATUS_COMMITTED, STATUS_MANDATORY_MISSING, STATUS_DELETED, STATUS_PENDING_CHANGES, STATUS_READ, \
    STATUS_READY_FOR_DELETION, STATUS_READY_FOR_MOVING, STATUS_READY_FOR_RENAMING, STATUS_VIRTUAL, STATUS_WRITABLE

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

    def test_create_entry_with_attribute_from_auxiliary_class(self):
        if test_server_type != 'AD':
            w = Writer(self.connection, 'inetorgperson', auxiliary_class='homeInfo')
            n = w.new('cn=' + testcase_id + 'new-1,' + test_base)
            n.sn = 'sn-test-1'
            n.homeState = 'state-test-1'
            self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
            n.entry_commit_changes()
            self.assertEqual(n.sn, 'sn-test-1')
            self.assertEqual(n.homeState, 'state-test-1')
            self.assertEqual(n.entry_status, STATUS_COMMITTED)
            n.entry_delete()
            self.assertEqual(n.entry_status, STATUS_READY_FOR_DELETION)
            n.entry_commit_changes()
            self.assertEqual(n.entry_status, STATUS_DELETED)

    def test_create_invalid_entry_with_attribute_from_auxiliary_class_not_declared(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-2,' + test_base)
        n.sn = 'sn-test-2'
        with self.assertRaises(LDAPCursorError):
            n.homeState = 'state-test-2'

    def test_read_entry_with_attribute_from_auxiliary_class(self):
        if test_server_type != 'AD':
            w = Writer(self.connection, 'inetorgperson', auxiliary_class='homeInfo')
            n = w.new('cn=' + testcase_id + 'new-3,' + test_base)
            n.sn = 'sn-test-3'
            n.homeState = 'state-test-3'
            self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
            n.entry_commit_changes()
            self.assertEqual(n.sn, 'sn-test-3')
            self.assertEqual(n.homeState, 'state-test-3')
            self.assertEqual(n.entry_status, STATUS_COMMITTED)

            r = Reader(self.connection, 'inetorgperson', test_base, '(cn=' + testcase_id + 'new-3', auxiliary_class='homeInfo')
            r.search()
            self.assertTrue(r[0].cn, testcase_id + 'new-3')
            self.assertTrue(r[0].homeState, testcase_id + 'state-test-3')

    def test_read_entry_with_attribute_from_missing_auxiliary_class(self):
        if test_server_type != 'AD':
            w = Writer(self.connection, 'inetorgperson', auxiliary_class='homeInfo')
            n = w.new('cn=' + testcase_id + 'new-4,' + test_base)
            n.sn = 'sn-test-4'
            n.homeState = 'state-test-4'
            self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
            n.entry_commit_changes()
            self.assertEqual(n.sn, 'sn-test-4')
            self.assertEqual(n.homeState, 'state-test-4')
            self.assertEqual(n.entry_status, STATUS_COMMITTED)

            r = Reader(self.connection, 'inetorgperson', test_base, '(cn=' + testcase_id + 'new-4')
            r.search()
            self.assertTrue(r[0].cn, testcase_id + 'new-4')
            with self.assertRaises(LDAPCursorError):
                self.assertTrue(r[0].homeState, testcase_id + 'state-test-3')
