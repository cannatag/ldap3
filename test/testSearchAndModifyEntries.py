"""
"""

# Created on 2016.08.20
#
# Author: Giovanni Cannata
#
# Copyright 2015 - 2018 Giovanni Cannata
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

from ldap3 import REUSABLE
from ldap3.core.exceptions import LDAPCursorError, LDAPOperationResult, LDAPConstraintViolationResult, LDAPAttributeOrValueExistsResult
from ldap3.abstract import STATUS_WRITABLE, STATUS_COMMITTED, STATUS_DELETED, STATUS_INIT, STATUS_MANDATORY_MISSING, STATUS_VIRTUAL, STATUS_PENDING_CHANGES, STATUS_READ, STATUS_READY_FOR_DELETION
from ldap3.core.results import RESULT_CONSTRAINT_VIOLATION, RESULT_ATTRIBUTE_OR_VALUE_EXISTS
from test.config import test_base, test_name_attr, random_id, get_connection, add_user, drop_connection, test_server_type, test_int_attr, test_strategy,\
    test_multivalued_attribute, test_singlevalued_attribute


testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()
        self.delete_at_teardown = []
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mod-1', attributes={test_multivalued_attribute: 'givenname-1', test_int_attr: 0}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mod-2', attributes={test_multivalued_attribute: ['givenname-2a', 'givenname-2b', 'givenname-2c'], test_int_attr: 0, test_singlevalued_attribute: 'init'}))
        elif test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mod-1', attributes={test_multivalued_attribute: 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mod-2', attributes={test_multivalued_attribute: ['givenname-2a', 'givenname-2b', 'givenname-2c'], test_singlevalued_attribute: 'init'}))
        else:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mod-1', attributes={test_multivalued_attribute: 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mod-2', attributes={test_multivalued_attribute: ['givenname-2a', 'givenname-2b', 'givenname-2c'], test_singlevalued_attribute: 'init'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def get_entry(self, entry_name):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + entry_name + ')', attributes=[test_name_attr, 'givenName', test_multivalued_attribute, test_singlevalued_attribute])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
            entries = self.connection._get_entries(response)
        else:
            result = self.connection.result
            entries = self.connection.entries
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(entries), 1)
        return entries[0]

    def compare_entries(self, entry1, entry2):
        for attr in entry1:
            self.assertFalse(entry1[attr.key] is entry2[attr.key])
            self.assertEqual(entry1[attr.key], entry2[attr.key])

        for attr in entry2:
            self.assertFalse(entry2[attr.key] is entry1[attr.key])
            self.assertEqual(entry2[attr.key], entry1[attr.key])

        for attr in entry1._state.attributes.keys():
            self.assertFalse(entry1._state.attributes[attr] is entry2._state.attributes[attr])
            self.assertEqual(entry1._state.attributes[attr], entry2._state.attributes[attr])

        for attr in entry2._state.attributes.keys():
            self.assertFalse(entry2._state.attributes[attr] is entry1._state.attributes[attr])
            self.assertEqual(entry2._state.attributes[attr], entry1._state.attributes[attr])

        for attr in entry1._state.raw_attributes.keys():
            self.assertFalse(entry1._state.raw_attributes[attr] is entry2._state.raw_attributes[attr])
            self.assertEqual(entry1._state.raw_attributes[attr], entry2._state.raw_attributes[attr])

        for attr in entry2._state.raw_attributes.keys():
            self.assertFalse(entry2._state.raw_attributes[attr] is entry1._state.raw_attributes[attr])
            self.assertEqual(entry2._state.raw_attributes[attr], entry1._state.raw_attributes[attr])

        self.assertEqual(entry1._state.dn, entry2._state.dn)
        self.assertEqual(entry1._state.response, entry2._state.response)
        self.assertEqual(entry1._state.read_time, entry2._state.read_time)

        self.assertFalse(entry1 is entry2)
        self.assertFalse(entry1._state is entry2._state)
        self.assertFalse(entry1._state.attributes is entry2._state.attributes)
        self.assertFalse(entry1._state.raw_attributes is entry2._state.raw_attributes)
        # if entry1._state.response is not None:
        #     self.assertFalse(entry1._state.response is entry2._state.response)
        # if entry1._state.read_time is not None:
        #     self.assertFalse(entry1._state.read_time is entry2._state.read_time)

    def test_search_and_delete_entry(self):
        add_user(self.connection, testcase_id, 'del1', attributes={'givenName': 'givenname-delete'})
        read_only_entry = self.get_entry('del1')
        self.assertEqual(read_only_entry.entry_status, STATUS_READ)
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        self.assertEqual(writable_entry.entry_status, STATUS_WRITABLE)
        writable_entry.entry_delete()
        self.assertEqual(writable_entry.entry_status, STATUS_READY_FOR_DELETION)
        result = writable_entry.entry_commit_changes()
        self.assertEqual(writable_entry.entry_status, STATUS_DELETED)
        self.assertTrue(result)
        counter = 20
        while counter > 0:  # waits for at maximum 20 times - delete operation can take some time to complete
            result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'del1)', attributes=[test_name_attr, 'givenName'])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
                entries = self.connection._get_entries(response)
            else:
                result = self.connection.result
                entries = self.connection.entries
            if len(entries) == 0:
                break
            sleep(3)
            counter -= 1

        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(entries), 0)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_value_to_existing_single_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute].add('single')
        writable_entry.entry_commit_changes()
        cursor = writable_entry.entry_cursor
        if not cursor.failed:
            self.fail('error assigning to existing single value')
        self.assertEqual(len(cursor.errors), 1)
        self.assertTrue(cursor.errors[0].result['result'] in [RESULT_CONSTRAINT_VIOLATION, RESULT_ATTRIBUTE_OR_VALUE_EXISTS])

    def test_search_and_implicit_add_value_to_existing_single_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute] += 'single'
        writable_entry.entry_commit_changes()
        cursor = writable_entry.entry_cursor
        if not cursor.failed:
            self.fail('error assigning to existing single value')
        self.assertEqual(len(cursor.errors), 1)
        self.assertTrue(cursor.errors[0].result['result'] in [RESULT_CONSTRAINT_VIOLATION, RESULT_ATTRIBUTE_OR_VALUE_EXISTS])

    def test_search_and_add_value_to_existing_single_value_with_exception(self):
        if test_strategy != REUSABLE:  # in REUSABLE strategy the connection can't be changed
            old_raise_exception = self.connection.raise_exceptions
            self.connection.raise_exceptions = True
            read_only_entry = self.get_entry('mod-2')
            writable_entry = read_only_entry.entry_writable('inetorgperson')
            writable_entry[test_singlevalued_attribute].add('single')
            try:
                writable_entry.entry_commit_changes()
            except (LDAPConstraintViolationResult, LDAPAttributeOrValueExistsResult):
                return
            finally:
                self.connection.raise_exceptions = old_raise_exception
            self.fail('error assigning to existing single value')

    def test_search_and_implicit_add_value_to_existing_single_value_with_exception(self):
        if test_strategy != REUSABLE:  # in REUSABLE strategy the connection can't be changed
            old_raise_exception = self.connection.raise_exceptions
            self.connection.raise_exceptions = True
            read_only_entry = self.get_entry('mod-2')
            writable_entry = read_only_entry.entry_writable('inetorgperson')
            writable_entry[test_singlevalued_attribute] += 'single'
            try:
                writable_entry.entry_commit_changes()
            except (LDAPConstraintViolationResult, LDAPAttributeOrValueExistsResult):
                return
            finally:
                self.connection.raise_exceptions = old_raise_exception
            self.fail('error assigning to existing single value')

    def test_search_and_add_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute].add('single')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute], 'single')
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson', attributes=[test_singlevalued_attribute])
        writable_entry[test_singlevalued_attribute] += 'single'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute], 'single')
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].add('added-givenname-1')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('added-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] += 'implicit-added-givenname-1'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('implicit-added-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].add('added-givenname-1')
        writable_entry[test_multivalued_attribute].add('added-givenname-2')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('added-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('added-givenname-2' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] += 'implicit-added-givenname-1'
        writable_entry[test_multivalued_attribute] += 'implicit-added-givenname-2'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('implicit-added-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('implicit-added-givenname-2' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].add(['added-givenname-1', 'added-givenname-2'])
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('added-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('added-givenname-2' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] += ['implicit-added-givenname-1', 'implicit-added-givenname-2']
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('implicit-added-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('implicit-added-givenname-2' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress.add('postalAddress-1')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress += 'postalAddress-1'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress.add('postalAddress-1')
        writable_entry.postalAddress.add('postalAddress-2')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress += 'postalAddress-1'
        writable_entry.postalAddress += 'postalAddress-2'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress.add(['postalAddress-1', 'postalAddress-2'])
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress += ['postalAddress-1', 'postalAddress-2']
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_existing_single_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute].set('single')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute], 'single')
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_existing_single_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute] = 'single'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute], 'single')
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute].set('init')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute], 'init')
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_singlevalued_attribute] = 'init'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute], 'init')
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].set('set-givenname-1')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('set-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] = 'implicit-set-givenname-1'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('implicit-set-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].set(['set-givenname-1', 'set-givenname-2'])
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('set-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('set-givenname-2' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] = ['implicit-set-givenname-1', 'implicit-set-givenname-2']
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('implicit-set-givenname-1' in writable_entry[test_multivalued_attribute])
        self.assertTrue('implicit-set-givenname-2' in writable_entry[test_multivalued_attribute])
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress.set('postalAddress-1')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress = 'postalAddress-1'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress.set(['postalAddress-1', 'postalAddress-2'])
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry.postalAddress = ['postalAddress-1', 'postalAddress-2']
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_remove_existing_attribute(self):
        read_only_entry = self.get_entry('mod-1')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].remove()
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_multivalued_attribute].values, [])
        self.assertEqual(writable_entry[test_multivalued_attribute].virtual, True)

    def test_search_and_delete_value_from_existing_single_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson', attributes='preferreddeliverymethod')
        writable_entry[test_singlevalued_attribute].delete('init')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute].value, None)
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 0)

    def test_search_and_implicit_delete_value_from_existing_single_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson', attributes='preferreddeliverymethod')
        writable_entry[test_singlevalued_attribute] -= 'init'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_singlevalued_attribute].value, None)
        self.assertEqual(len(writable_entry[test_singlevalued_attribute]), 0)

    def test_search_and_delete_value_from_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].delete('givenname-2a')
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-2b' in writable_entry[test_multivalued_attribute].value)
        self.assertTrue('givenname-2c' in writable_entry[test_multivalued_attribute].value)
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 2)

    def test_search_and_implicit_delete_value_from_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] -= 'givenname-2a'
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-2b' in writable_entry[test_multivalued_attribute].value)
        self.assertTrue('givenname-2c' in writable_entry[test_multivalued_attribute].value)
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 2)

    def test_search_and_delete_values_from_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].delete(['givenname-2a', 'givenname-2b'])
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-2c' in writable_entry[test_multivalued_attribute].value)
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 1)

    def test_search_and_implicit_delete_values_from_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] -= ['givenname-2a', 'givenname-2b']
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertTrue('givenname-2c' in writable_entry[test_multivalued_attribute].value)
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 1)

    def test_search_and_delete_all_values_from_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute].delete(['givenname-2a', 'givenname-2b', 'givenname-2c'])
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_multivalued_attribute].value, None)
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 0)

    def test_search_and_implicit_delete_all_values_from_existing_multi_value(self):
        read_only_entry = self.get_entry('mod-2')
        writable_entry = read_only_entry.entry_writable('inetorgperson')
        writable_entry[test_multivalued_attribute] -= ['givenname-2a', 'givenname-2b', 'givenname-2c']
        result = writable_entry.entry_commit_changes()
        self.assertTrue(result)
        self.assertEqual(writable_entry[test_multivalued_attribute].value, None)
        self.assertEqual(len(writable_entry[test_multivalued_attribute]), 0)

    def test_search_and_add_value_to_existing_multi_value_using_alias(self):
        if test_server_type != 'AD':  # AD doens't use alias for cn
            read_only_entry = self.get_entry('mod-1')
            writable_entry = read_only_entry.entry_writable('inetorgperson')
            self.assertTrue(testcase_id + 'mod-1' in writable_entry.cn)
            self.assertTrue(testcase_id + 'mod-1' in writable_entry.commonname)
            writable_entry.commonname.add('added-commonname-1')
            result = writable_entry.entry_commit_changes()
            self.assertTrue(result)
            self.assertTrue('added-commonname-1' in writable_entry.cn)
            self.assertTrue('added-commonname-1' in writable_entry.commonname)
            self.assertEqual(len(writable_entry.commonname), 2)
            self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_existing_multi_value_using_alias(self):
        if test_server_type != 'AD':  # AD doens't use alias for cn
            read_only_entry = self.get_entry('mod-1')
            writable_entry = read_only_entry.entry_writable('inetorgperson')
            self.assertTrue(testcase_id + 'mod-1' in writable_entry.cn)
            self.assertTrue(testcase_id + 'mod-1' in writable_entry.commonname)
            writable_entry.commonname += 'implicit-added-commonname-1'
            result = writable_entry.entry_commit_changes()
            self.assertTrue(result)
            self.assertTrue('givenname-1' in writable_entry[test_multivalued_attribute])
            self.assertTrue('implicit-added-commonname-1' in writable_entry.cn)
            self.assertTrue('implicit-added-commonname-1' in writable_entry.commonname)
            self.assertEqual(len(writable_entry.commonname), 2)
            self.compare_entries(read_only_entry, writable_entry)

