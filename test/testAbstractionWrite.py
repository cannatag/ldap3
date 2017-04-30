"""
"""
# Created on 2014.01.19
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016 Giovanni Cannata
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

    def test_create_new_entry_invalid_mandatory(self):
        if test_server_type == 'EDIR':
            w = Writer(self.connection, 'inetorgperson')
            n = w.new('cn=' + testcase_id + 'new-1,' + test_base)
            self.assertTrue('sn' in n.entry_mandatory_attributes)
            self.assertTrue(n.entry_status in [STATUS_MANDATORY_MISSING])
            try:
                n.entry_commit_changes()
            except LDAPCursorError:
                return
            self.fail('Entry created with missing attributes')

    def test_create_new_entry_valid_mandatory_only(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-2,' + test_base)
        n.sn = 'sn-test-2'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        n.entry_commit_changes()
        self.assertEqual(n.sn, 'sn-test-2')
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_delete()
        self.assertEqual(n.entry_status, STATUS_READY_FOR_DELETION)
        n.entry_commit_changes()
        self.assertEqual(n.entry_status, STATUS_DELETED)

    def test_create_new_entry_valid_mandatory_and_optional(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-3,' + test_base)
        n.sn = 'sn-test-3'
        n.postalAddress = 'postal-address-3'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        n.entry_commit_changes()
        self.assertEqual(n.sn, 'sn-test-3')
        self.assertEqual(n.postalAddress, 'postal-address-3')
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_delete()
        self.assertEqual(n.entry_status, STATUS_READY_FOR_DELETION)
        n.entry_commit_changes()
        self.assertEqual(n.entry_status, STATUS_DELETED)

    def test_create_new_entry_valid_and_rename_before_commit(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-4,' + test_base)
        n.sn = 'sn-test-4'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        try:
            n.entry_rename('cn=' + testcase_id + 'new-4-renamed')
        except LDAPCursorError:
            pass

    def test_create_new_entry_valid_and_rename_after_commit(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-5,' + test_base)
        n.sn = 'sn-test-5'
        n.postalAddress = 'postal-address-5'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        n.entry_commit_changes()
        self.assertEqual(n.sn, 'sn-test-5')
        self.assertEqual(n.postalAddress, 'postal-address-5')
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_rename('cn=' + testcase_id + 'new-5-renamed')
        self.assertEqual(n.entry_status, STATUS_READY_FOR_RENAMING)
        n.entry_commit_changes()
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_delete()
        self.assertEqual(n.entry_status, STATUS_READY_FOR_DELETION)
        n.entry_commit_changes()
        self.assertEqual(n.entry_status, STATUS_DELETED)

    def test_create_new_entry_valid_and_move_before_commit(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-6,' + test_base)
        n.sn = 'sn-test-6'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        try:
            n.entry_move(test_moved)
        except LDAPCursorError:
            pass

    def test_create_new_entry_valid_and_move_after_commit(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('cn=' + testcase_id + 'new-7,' + test_base)
        n.sn = 'sn-test-7'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        n.entry_commit_changes()
        self.assertEqual(n.sn, 'sn-test-7')
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_move(test_moved)
        self.assertEqual(n.entry_status, STATUS_READY_FOR_MOVING)
        sleep(5)
        n.entry_commit_changes()
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_delete()
        self.assertEqual(n.entry_status, STATUS_READY_FOR_DELETION)
        counter = 20
        while counter > 0:
            try:
                n.entry_commit_changes()
                if n.entry_status == STATUS_DELETED:
                    break
            except LDAPCursorError:
                pass
            counter -= 1
            sleep(3)
        self.assertEqual(n.entry_status, STATUS_DELETED)

    def test_create_new_entry_valid_mandatory_only_case_insensitive_attribute_names(self):
        w = Writer(self.connection, 'inetorgperson')
        n = w.new('CN=' + testcase_id + 'new-8,' + test_base)
        n.sn = 'sn-test-8'
        self.assertEqual(n.entry_status, STATUS_PENDING_CHANGES)
        n.entry_commit_changes()
        self.assertEqual(n.sn, 'sn-test-8')
        self.assertEqual(n.entry_status, STATUS_COMMITTED)
        n.entry_delete()
        self.assertEqual(n.entry_status, STATUS_READY_FOR_DELETION)
        n.entry_commit_changes()
        self.assertEqual(n.entry_status, STATUS_DELETED)

    def test_modify_entry_with_attrdef_with_friendly_name(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'new-9', attributes={test_multivalued_attribute: testcase_id + 'friendly-attr-name-1'}))
        a = AttrDef(name=test_multivalued_attribute, key='myname')
        o = ObjectDef('inetorgperson')
        o += a
        r = Reader(self.connection, o, test_base, 'myname:=' + testcase_id + 'friendly*')
        r.search()
        self.assertTrue(r[0].myname, testcase_id + 'friendly-attr-name-1')
        w = Writer.from_cursor(r)
        e = w[0]
        e.myname += 'xyz'
        w.commit()
        self.assertTrue('xyz' in e.myname)
