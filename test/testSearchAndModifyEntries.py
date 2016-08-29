"""
"""

# Created on 2016.08.20
#
# Author: Giovanni Cannata
#
# Copyright 2015, 2016 Giovanni Cannata
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

from ldap3.core.exceptions import LDAPEntryError
from test import test_base, test_name_attr, random_id, get_connection, \
    add_user, drop_connection, test_server_type, test_int_attr

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        if test_server_type == 'EDIR':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-1', attributes={'givenName': 'givenname-1', test_int_attr: 0}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-2', attributes={'givenName': 'givenname-2', test_int_attr: 0, 'preferredDeliveryMethod': 'any'}))
        elif test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-2', attributes={'givenName': 'givenname-2'}))
        else:
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-and-modify-2', attributes={'givenName': 'givenname-2'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def get_entry(self, entry_name):
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + entry_name + ')', attributes=[test_name_attr, 'givenName'])
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
        if entry1._state.response is not None:
            self.assertFalse(entry1._state.response is entry2._state.response)
        if entry1._state.read_time is not None:
            self.assertFalse(entry1._state.read_time is entry2._state.read_time)

    def test_duplicate_entry(self):
        entry1 = self.get_entry('search-and-modify-1')
        entry2 = entry1.entry_duplicate()
        self.compare_entries(entry1, entry2)

    def test_search_and_delete_entry(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        result = writable_entry.entry_delete()
        self.assertTrue(result)
        result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-and-modify-1)', attributes=[test_name_attr, 'givenName'])
        if not self.connection.strategy.sync:
            response, result = self.connection.get_response(result)
            entries = self.connection._get_entries(response)
        else:
            result = self.connection.result
            entries = self.connection.entries
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(entries), 0)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_value_to_existing_single_value(self):
        if test_server_type == 'EDIR':
            read_only_entry = self.get_entry('search-and-modify-2')
            writable_entry = read_only_entry.make_writable('inetorgperson')
            writable_entry.preferredDeliveryMethod.add_value('telephone')
            try:
                writable_entry.entry_commit()
            except LDAPEntryError as e:
                self.assertEqual(self.connection.result['description'], 'constraintViolation')
                return
            self.fail('error assigning to existing single value')

    def test_search_and_implicit_add_value_to_existing_single_value(self):
        if test_server_type == 'EDIR':
            read_only_entry = self.get_entry('search-and-modify-2')
            writable_entry = read_only_entry.make_writable('inetorgperson')
            writable_entry.preferredDeliveryMethod += 'telephone'
            try:
                writable_entry.entry_commit()
            except LDAPEntryError as e:
                self.assertEqual(self.connection.result['description'], 'constraintViolation')
                return
            self.fail('error assigning to existing single value')

    def test_search_and_add_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.preferredDeliveryMethod.add_value('any')  # single valued in organizationalPerson, defined in rfc4519
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertEqual(writable_entry.preferredDeliveryMethod, 'any')
        self.assertEqual(len(writable_entry.preferredDeliveryMethod), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.preferreddeliverymethod += 'any'  # single valued in organizationalPerson, defined in rfc4519
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertEqual(writable_entry.preferredDeliveryMethod, 'any')
        self.assertEqual(len(writable_entry.preferredDeliveryMethod), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname.add_value('added-givenname-1')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry.givenName)
        self.assertTrue('added-givenname-1' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname += 'implicit-added-givenname-1'
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry.givenName)
        self.assertTrue('implicit-added-givenname-1' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname.add_value('added-givenname-1')
        writable_entry.givenname.add_value('added-givenname-2')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry.givenName)
        self.assertTrue('added-givenname-1' in writable_entry.givenName)
        self.assertTrue('added-givenname-2' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname += 'implicit-added-givenname-1'
        writable_entry.givenname += 'implicit-added-givenname-2'
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry.givenName)
        self.assertTrue('implicit-added-givenname-1' in writable_entry.givenName)
        self.assertTrue('implicit-added-givenname-2' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname.add_value(['added-givenname-1', 'added-givenname-2'])
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry.givenName)
        self.assertTrue('added-givenname-1' in writable_entry.givenName)
        self.assertTrue('added-givenname-2' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 3)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname += ['implicit-added-givenname-1', 'implicit-added-givenname-2']
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('givenname-1' in writable_entry.givenName)
        self.assertTrue('implicit-added-givenname-1' in writable_entry.givenName)
        self.assertTrue('implicit-added-givenname-2' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 3)
        self.compare_entries(read_only_entry, writable_entry)


    def test_search_and_add_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress.add_value('postalAddress-1')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress += 'postalAddress-1'
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress.add_value('postalAddress-1')
        writable_entry.postalAddress.add_value('postalAddress-2')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress += 'postalAddress-1'
        writable_entry.postalAddress += 'postalAddress-2'
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_add_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress.add_value(['postalAddress-1', 'postalAddress-2'])
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_add_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress += ['postalAddress-1', 'postalAddress-2']
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_existing_single_value(self):
        if test_server_type == 'EDIR':
            read_only_entry = self.get_entry('search-and-modify-2')
            writable_entry = read_only_entry.make_writable('inetorgperson')
            writable_entry.preferredDeliveryMethod.set_value('telephone')
            result = writable_entry.entry_commit()
            self.assertTrue(result)
            self.assertEqual(writable_entry.preferredDeliveryMethod, 'telephone')
            self.assertEqual(len(writable_entry.preferredDeliveryMethod), 1)
            self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_existing_single_value(self):
        if test_server_type == 'EDIR':
            read_only_entry = self.get_entry('search-and-modify-2')
            writable_entry = read_only_entry.make_writable('inetorgperson')
            writable_entry.preferredDeliveryMethod = 'telephone'
            result = writable_entry.entry_commit()
            self.assertTrue(result)
            self.assertEqual(writable_entry.preferredDeliveryMethod, 'telephone')
            self.assertEqual(len(writable_entry.preferredDeliveryMethod), 1)
            self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.preferredDeliveryMethod.set_value('any')  # single valued in organizationalPerson, defined in rfc4519
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertEqual(writable_entry.preferredDeliveryMethod, 'any')
        self.assertEqual(len(writable_entry.preferredDeliveryMethod), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_non_existing_single_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.preferreddeliverymethod = 'any'  # single valued in organizationalPerson, defined in rfc4519
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertEqual(writable_entry.preferredDeliveryMethod, 'any')
        self.assertEqual(len(writable_entry.preferredDeliveryMethod), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname.set_value('set-givenname-1')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('set-givenname-1' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname = 'implicit-set-givenname-1'
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('implicit-set-givenname-1' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname.set_value(['set-givenname-1', 'set-givenname-2'])
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('set-givenname-1' in writable_entry.givenName)
        self.assertTrue('set-givenname-2' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_values_from_sequence_to_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.givenname = ['implicit-set-givenname-1', 'implicit-set-givenname-2']
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('implicit-set-givenname-1' in writable_entry.givenName)
        self.assertTrue('implicit-set-givenname-2' in writable_entry.givenName)
        self.assertEqual(len(writable_entry.givenname), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress.set_value('postalAddress-1')
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_value_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress = 'postalAddress-1'
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 1)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_set_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress.set_value(['postalAddress-1', 'postalAddress-2'])
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_implicit_set_values_from_sequence_to_non_existing_multi_value(self):
        read_only_entry = self.get_entry('search-and-modify-1')
        writable_entry = read_only_entry.make_writable('inetorgperson')
        writable_entry.postalAddress = ['postalAddress-1', 'postalAddress-2']
        result = writable_entry.entry_commit()
        self.assertTrue(result)
        self.assertTrue('postalAddress-1' in writable_entry.postalAddress)
        self.assertTrue('postalAddress-2' in writable_entry.postalAddress)
        self.assertEqual(len(writable_entry.postalAddress), 2)
        self.compare_entries(read_only_entry, writable_entry)

    def test_search_and_delete_value_to_existing_single_value(self):
        if test_server_type == 'EDIR':
            read_only_entry = self.get_entry('search-and-modify-2')
            writable_entry = read_only_entry.make_writable('inetorgperson', attributes='preferreddeliverymethod')
            writable_entry.preferredDeliveryMethod.delete_value('any')
            result = writable_entry.entry_commit()
            self.assertTrue(result)
            self.assertEqual(writable_entry.preferredDeliveryMethod.value, None)
            self.assertEqual(len(writable_entry.preferredDeliveryMethod), 0)
            self.compare_entries(read_only_entry, writable_entry)

