# Created on 2015.02.3
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

from ldap3 import Server, Connection, MOCK_SYNC, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, OFFLINE_SLAPD_2_4, BASE, LEVEL, SUBTREE
from ldap3.protocol.rfc4512 import SchemaInfo, DsaInfo
from ldap3.protocol.schemas.edir888 import edir_8_8_8_dsa_info, edir_8_8_8_schema
from test import random_id

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        # The mock server can be defined in two different ways, so tests are duplicated
        schema = SchemaInfo.from_json(edir_8_8_8_schema)
        info = DsaInfo.from_json(edir_8_8_8_dsa_info, schema)
        server_1 = Server.from_definition('MockSyncServer', info, schema)
        self.connection_1 = Connection(server_1, user='cn=user1,ou=test,o=lab', password='test1111', client_strategy=MOCK_SYNC)
        server_2 = Server('dummy', get_info=OFFLINE_SLAPD_2_4)
        self.connection_2 = Connection(server_2, user='cn=user2,ou=test,o=lab', password='test2222', client_strategy=MOCK_SYNC)
        server_3 = Server('dummy')
        self.connection_3 = Connection(server_3, user='cn=user3,ou=test,o=lab', password='test3333', client_strategy=MOCK_SYNC)
        self.connection_1.strategy.entries_from_json('mock_entries.json')
        self.connection_2.strategy.entries_from_json('mock_entries.json')
        self.connection_3.strategy.entries_from_json('mock_entries.json')

    def tearDown(self):
        self.connection_1.unbind()
        self.assertFalse(self.connection_1.bound)
        self.connection_2.unbind()
        self.assertFalse(self.connection_2.bound)
        self.connection_3.unbind()
        self.assertFalse(self.connection_3.bound)

    def test_open_1(self):
        self.connection_1.open()
        self.assertFalse(self.connection_1.closed)

    def test_open_2(self):
        self.connection_2.open()
        self.assertFalse(self.connection_2.closed)

    def test_open_3(self):
        self.connection_3.open()
        self.assertFalse(self.connection_3.closed)

    def test_bind_1(self):
        self.connection_1.open()
        self.connection_1.bind()
        self.assertTrue(self.connection_1.bound)

    def test_bind_2(self):
        self.connection_2.open()
        self.connection_2.bind()
        self.assertTrue(self.connection_2.bound)

    def test_bind_3(self):
        self.connection_3.open()
        self.connection_3.bind()
        self.assertTrue(self.connection_3.bound)

    def test_unbind_1(self):
        self.connection_1.open()
        self.assertFalse(self.connection_1.closed)
        self.connection_1.bind()
        self.assertTrue(self.connection_1.bound)
        self.connection_1.unbind()
        self.assertFalse(self.connection_1.bound)
        self.assertTrue(self.connection_1.closed)

    def test_unbind_2(self):
        self.connection_2.open()
        self.assertFalse(self.connection_2.closed)
        self.connection_2.bind()
        self.assertTrue(self.connection_2.bound)
        self.connection_2.unbind()
        self.assertFalse(self.connection_2.bound)
        self.assertTrue(self.connection_2.closed)

    def test_unbind_3(self):
        self.connection_3.open()
        self.assertFalse(self.connection_3.closed)
        self.connection_3.bind()
        self.assertTrue(self.connection_3.bound)
        self.connection_3.unbind()
        self.assertFalse(self.connection_3.bound)
        self.assertTrue(self.connection_3.closed)

    def test_delete_1(self):
        self.connection_1.bind()
        self.connection_1.delete('cn=admin,o=resources')
        self.assertTrue(self.connection_1.result['description'], 'success')

    def test_delete_2(self):
        self.connection_2.bind()
        self.connection_2.delete('cn=admin,o=resources')
        self.assertTrue(self.connection_2.result['description'], 'success')

    def test_delete_3(self):
        self.connection_3.bind()
        self.connection_3.delete('cn=admin,o=resources')
        self.assertTrue(self.connection_3.result['description'], 'success')

    def test_add_user_1(self):
        self.connection_1.strategy.add_entry('cn=user4,ou=test,o=lab', {'userPassword': 'test4444'})
        self.connection_1.rebind('cn=user4,ou=test,o=lab', 'test4444')
        self.assertTrue(self.connection_1.bound)

    def test_add_user_2(self):
        self.connection_2.strategy.add_entry('cn=user4,ou=test,o=lab', {'userPassword': 'test4444'})
        self.connection_2.rebind('cn=user4,ou=test,o=lab', 'test4444')
        self.assertTrue(self.connection_2.bound)

    def test_add_user_3(self):
        self.connection_3.strategy.add_entry('cn=user4,ou=test,o=lab', {'userPassword': 'test4444'})
        self.connection_3.rebind('cn=user4,ou=test,o=lab', 'test4444')
        self.assertTrue(self.connection_3.bound)

    def test_remove_user_1(self):
        self.connection_1.strategy.remove_entry('cn=user2,ou=test,o=lab')
        self.connection_1.bind()
        self.assertTrue(self.connection_1.bound)
        self.connection_1.rebind('cn=user2,ou=test,o=lab', 'test9876')
        self.assertFalse(self.connection_1.bound)

    def test_remove_user_2(self):
        self.connection_2.strategy.remove_entry('cn=user1,ou=test,o=lab')
        self.connection_2.bind()
        self.assertTrue(self.connection_2.bound)
        self.connection_2.rebind('cn=user1,ou=test,o=lab', 'test9876')
        self.assertFalse(self.connection_1.bound)

    def test_remove_user_3(self):
        self.connection_3.strategy.remove_entry('cn=user1,ou=test,o=lab')
        self.connection_3.bind()
        self.assertTrue(self.connection_3.bound)
        self.connection_3.rebind('cn=user1,ou=test,o=lab', 'test1111')
        self.assertFalse(self.connection_1.bound)

    def test_add_entry_1(self):
        self.connection_1.bind()
        self.connection_1.add('cn=user_test,ou=test,o=lab', ['inetOrgPerson', 'top'], {'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_1.strategy.entries)

    def test_add_entry_2(self):
        self.connection_2.bind()
        self.connection_2.add('cn=user_test,ou=test,o=lab', ['inetOrgPerson', 'top'], {'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_2.strategy.entries)

    def test_add_entry_3(self):
        self.connection_3.bind()
        self.connection_3.add('cn=user_test,ou=test,o=lab', ['inetOrgPerson', 'top'], {'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_3.strategy.entries)

    def test_add_entry_already_exists_1(self):
        self.connection_1.bind()
        self.connection_1.strategy.add_entry('cn=user_test,ou=test,o=lab', {'objectClass': ['inetOrgPerson', 'top'], 'sn': 'user_test_sn'})
        self.connection_1.add('cn=user_test,ou=test,o=lab', ['inetOrgPerson', 'top'], {'sn': 'user_test_sn'})
        self.assertEqual(self.connection_1.result['description'], 'entryAlreadyExists')

    def test_add_entry_already_exists_2(self):
        self.connection_2.bind()
        self.connection_2.strategy.add_entry('cn=user_test,ou=test,o=lab', {'objectClass': ['inetOrgPerson', 'top'], 'sn': 'user_test_sn'})
        self.connection_2.add('cn=user_test,ou=test,o=lab', ['inetOrgPerson', 'top'], {'sn': 'user_test_sn'})
        self.assertEqual(self.connection_2.result['description'], 'entryAlreadyExists')

    def test_add_entry_already_exists_3(self):
        self.connection_3.bind()
        self.connection_3.strategy.add_entry('cn=user_test,ou=test,o=lab', {'objectClass': ['inetOrgPerson', 'top'], 'sn': 'user_test_sn'})
        self.connection_3.add('cn=user_test,ou=test,o=lab', ['inetOrgPerson', 'top'], {'sn': 'user_test_sn'})
        self.assertEqual(self.connection_3.result['description'], 'entryAlreadyExists')

    def test_delete_entry_1(self):
        self.connection_1.bind()
        self.connection_1.delete('cn=admin,o=resources')
        self.assertTrue('cn=admin,o=resources' not in self.connection_1.strategy.entries)

    def test_delete_entry_2(self):
        self.connection_2.bind()
        self.connection_2.delete('cn=admin,o=resources')
        self.assertTrue('cn=admin,o=resources' not in self.connection_2.strategy.entries)

    def test_delete_entry_3(self):
        self.connection_3.bind()
        self.connection_3.delete('cn=admin,o=resources')
        self.assertTrue('cn=admin,o=resources' not in self.connection_3.strategy.entries)

    def test_delete_entry_nonexisting_1(self):
        self.connection_1.bind()
        self.connection_1.strategy.remove_entry('cn=admin,o=resources')
        self.assertTrue('cn=admin,o=resources' not in self.connection_1.strategy.entries)
        self.connection_1.delete('cn=admin,o=resources')
        self.assertEqual(self.connection_1.result['description'], 'noSuchObject')

    def test_delete_entry_nonexisting_2(self):
        self.connection_2.bind()
        self.connection_2.strategy.remove_entry('cn=admin,o=resources')
        self.assertTrue('cn=admin,o=resources' not in self.connection_2.strategy.entries)
        self.connection_2.delete('cn=admin,o=resources')
        self.assertEqual(self.connection_2.result['description'], 'noSuchObject')

    def test_delete_entry_nonexisting_3(self):
        self.connection_3.bind()
        self.connection_3.strategy.remove_entry('cn=admin,o=resources')
        self.assertTrue('cn=admin,o=resources' not in self.connection_3.strategy.entries)
        self.connection_3.delete('cn=admin,o=resources')
        self.assertEqual(self.connection_3.result['description'], 'noSuchObject')

    def test_compare_entry_1(self):
        self.connection_1.bind()
        self.connection_1.compare('cn=admin,o=resources', 'sn', 'admin')
        self.assertTrue(self.connection_1.result['description'], 'compareTrue')
        self.connection_1.compare('cn=admin,o=resources', 'sn', 'bad_value')
        self.assertTrue(self.connection_1.result['description'], 'compareFalse')

    def test_compare_entry_2(self):
        self.connection_2.bind()
        self.connection_2.compare('cn=admin,o=resources', 'sn', 'admin')
        self.assertTrue(self.connection_2.result['description'], 'compareTrue')
        self.connection_2.compare('cn=admin,o=resources', 'sn', 'bad_value')
        self.assertTrue(self.connection_2.result['description'], 'compareFalse')

    def test_compare_entry_3(self):
        self.connection_3.bind()
        self.connection_3.compare('cn=admin,o=resources', 'sn', 'admin')
        self.assertTrue(self.connection_3.result['description'], 'compareTrue')
        self.connection_3.compare('cn=admin,o=resources', 'sn', 'bad_value')
        self.assertTrue(self.connection_3.result['description'], 'compareFalse')

    def test_move_dn_1(self):
        self.connection_1.bind()
        self.connection_1.add('cn=user_test,ou=test,o=lab', 'inetOrgPerson', attributes = {'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_1.strategy.entries)
        self.connection_1.modify_dn('cn=user_test,ou=test,o=lab', relative_dn='cn=user_test', new_superior='ou=moved,o=lab')
        self.assertTrue('cn=user_test,ou=moved,o=lab' in self.connection_1.strategy.entries)
        self.assertFalse('cn=user_test,ou=test,o=lab' in self.connection_1.strategy.entries)

    def test_move_dn_2(self):
        self.connection_2.bind()
        self.connection_2.add('cn=user_test,ou=test,o=lab', 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_2.strategy.entries)
        self.connection_2.modify_dn('cn=user_test,ou=test,o=lab', relative_dn='cn=user_test', new_superior='ou=moved,o=lab')
        self.assertTrue('cn=user_test,ou=moved,o=lab' in self.connection_2.strategy.entries)
        self.assertFalse('cn=user,ou=test,o=lab' in self.connection_2.strategy.entries)

    def test_move_dn_3(self):
        self.connection_3.bind()
        self.connection_3.add('cn=user_test,ou=test,o=lab', 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_3.strategy.entries)
        self.connection_3.modify_dn('cn=user_test,ou=test,o=lab', relative_dn='cn=user_test', new_superior='ou=moved,o=lab')
        self.assertTrue('cn=user_test,ou=moved,o=lab' in self.connection_3.strategy.entries)
        self.assertFalse('cn=user_test,ou=test,o=lab' in self.connection_3.strategy.entries)

    def test_rename_dn_1(self):
        self.connection_1.bind()
        self.connection_1.add('cn=user_test,ou=test,o=lab', 'inetOrgPerson', attributes = {'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_1.strategy.entries)
        self.connection_1.modify_dn('cn=user_test,ou=test,o=lab', relative_dn='cn=user_test_renamed')
        self.assertTrue('cn=user_test_renamed,ou=test,o=lab' in self.connection_1.strategy.entries)
        self.assertFalse('cn=user_test,ou=test,o=lab' in self.connection_1.strategy.entries)

    def test_rename_dn_2(self):
        self.connection_2.bind()
        self.connection_2.add('cn=user_test,ou=test,o=lab', 'inetOrgPerson', attributes = {'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_2.strategy.entries)
        self.connection_2.modify_dn('cn=user_test,ou=test,o=lab', relative_dn='cn=user_test_renamed')
        self.assertTrue('cn=user_test_renamed,ou=test,o=lab' in self.connection_2.strategy.entries)
        self.assertFalse('cn=user_test,ou=test,o=lab' in self.connection_2.strategy.entries)

    def test_rename_dn_3(self):
        self.connection_3.bind()
        self.connection_3.add('cn=user_test,ou=test,o=lab', 'inetOrgPerson', attributes = {'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue('cn=user_test,ou=test,o=lab' in self.connection_3.strategy.entries)
        self.connection_3.modify_dn('cn=user_test,ou=test,o=lab', relative_dn='cn=user_test_renamed')
        self.assertTrue('cn=user_test_renamed,ou=test,o=lab' in self.connection_3.strategy.entries)
        self.assertFalse('cn=user_test,ou=test,o=lab' in self.connection_1.strategy.entries)

    def test_modify_add_existing_singlevalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'sn': (MODIFY_ADD, ['sn_added'])})
        self.assertTrue('sn_added' in self.connection_1.strategy.entries[dn]['sn'])

    def test_modify_add_existing_singlevalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'sn': (MODIFY_ADD, ['sn_added'])})
        self.assertTrue('sn_added' in self.connection_2.strategy.entries[dn]['sn'])

    def test_modify_add_existing_singlevalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'sn': (MODIFY_ADD, ['sn_added'])})
        self.assertTrue('sn_added' in self.connection_3.strategy.entries[dn]['sn'])

    def test_modify_add_nonexisting_singlevalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_ADD, ['title_added'])})
        self.assertTrue('title_added' in self.connection_1.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_singlevalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_ADD, ['title_added'])})
        self.assertTrue('title_added' in self.connection_2.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_singlevalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_ADD, ['title_added'])})
        self.assertTrue('title_added' in self.connection_3.strategy.entries[dn]['title'])

    def test_modify_add_existing_multivalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'sn': (MODIFY_ADD, ['sn_added1', 'sn_added2'])})
        self.assertTrue('sn_added1' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertTrue('sn_added2' in self.connection_1.strategy.entries[dn]['sn'])

    def test_modify_add_existing_multivalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'sn': (MODIFY_ADD, ['sn_added1', 'sn_added2'])})
        self.assertTrue('sn_added1' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertTrue('sn_added2' in self.connection_2.strategy.entries[dn]['sn'])

    def test_modify_add_existing_multivalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'sn': (MODIFY_ADD, ['sn_added1', 'sn_added3'])})
        self.assertTrue('sn_added1' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertTrue('sn_added3' in self.connection_3.strategy.entries[dn]['sn'])

    def test_modify_add_nonexisting_multivalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_ADD, ['title_added1', 'title_added2'])})
        self.assertTrue('title_added1' in self.connection_1.strategy.entries[dn]['title'])
        self.assertTrue('title_added2' in self.connection_1.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_multivalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_ADD, ['title_added1', 'title_added2'])})
        self.assertTrue('title_added1' in self.connection_2.strategy.entries[dn]['title'])
        self.assertTrue('title_added2' in self.connection_2.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_multivalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_ADD, ['title_added1', 'title_added3'])})
        self.assertTrue('title_added1' in self.connection_3.strategy.entries[dn]['title'])
        self.assertTrue('title_added3' in self.connection_3.strategy.entries[dn]['title'])

    def test_modify_delete_nonexisting_attribute_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_DELETE, ['title_added1', 'title_added2'])})
        self.assertEqual(self.connection_1.result['description'], 'noSuchAttribute')

    def test_modify_delete_nonexisting_attribute_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_DELETE, ['title_added1', 'title_added2'])})
        self.assertEqual(self.connection_2.result['description'], 'noSuchAttribute')

    def test_modify_delete_nonexisting_attribute_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_DELETE, ['title_added1', 'title_added3'])})
        self.assertEqual(self.connection_3.result['description'], 'noSuchAttribute')

    def test_modify_delete_existing_singlevalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'sn': (MODIFY_DELETE, ['user_test_sn'])})
        self.assertEqual(self.connection_1.result['description'], 'success')

    def test_modify_delete_existing_singlevalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'sn': (MODIFY_DELETE, ['user_test_sn'])})
        self.assertEqual(self.connection_2.result['description'], 'success')

    def test_modify_delete_existing_singlevalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'sn': (MODIFY_DELETE, ['user_test_sn'])})
        self.assertEqual(self.connection_3.result['description'], 'success')

    def test_modify_delete_existing_multivalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': ['user_test_sn1', 'user_test_sn2', 'user_test_sn3']})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'sn': (MODIFY_DELETE, ['user_test_sn1', 'user_test_sn2'])})
        self.assertEqual(self.connection_1.result['description'], 'success')

    def test_modify_delete_existing_multivalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': ['user_test_sn1', 'user_test_sn2', 'user_test_sn3']})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'sn': (MODIFY_DELETE, ['user_test_sn1', 'user_test_sn2'])})
        self.assertEqual(self.connection_2.result['description'], 'success')

    def test_modify_delete_existing_multivalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': ['user_test_sn1', 'user_test_sn3', 'user_test_sn3']})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'sn': (MODIFY_DELETE, ['user_test_sn1', 'user_test_sn3'])})
        self.assertEqual(self.connection_3.result['description'], 'success')

    def test_modify_replace_existing_singlevalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn1'])})
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertTrue('user_test_sn1' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_1.strategy.entries[dn]['sn']), 1)

    def test_modify_replace_existing_singlevalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn1'])})
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertTrue('user_test_sn1' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_2.strategy.entries[dn]['sn']), 1)

    def test_modify_replace_existing_singlevalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn1'])})
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertTrue('user_test_sn1' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_3.strategy.entries[dn]['sn']), 1)

    def test_modify_replace_existing_multivalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': ['user_test_sn1', 'user_test_sn2', 'user_test_sn3']})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn4', 'user_test_sn5'])})
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertFalse('user_test_sn1' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertFalse('user_test_sn2' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertFalse('user_test_sn3' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertTrue('user_test_sn4' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertTrue('user_test_sn5' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_1.strategy.entries[dn]['sn']), 2)

    def test_modify_replace_existing_multivalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': ['user_test_sn1', 'user_test_sn2', 'user_test_sn3']})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn4', 'user_test_sn5'])})
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertFalse('user_test_sn1' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertFalse('user_test_sn2' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertFalse('user_test_sn3' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertTrue('user_test_sn4' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertTrue('user_test_sn5' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_2.strategy.entries[dn]['sn']), 2)

    def test_modify_replace_existing_multivalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': ['user_test_sn1', 'user_test_sn3', 'user_test_sn3']})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn4', 'user_test_sn5'])})
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertFalse('user_test_sn1' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertFalse('user_test_sn3' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertFalse('user_test_sn3' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertTrue('user_test_sn4' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertTrue('user_test_sn5' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_3.strategy.entries[dn]['sn']), 2)

    def test_modify_replace_existing_novalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn', 'title': ['title1', 'title2']})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_REPLACE, [])})
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertFalse('title' in self.connection_1.strategy.entries[dn])

    def test_modify_replace_existing_novalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn', 'title': ['title1', 'title2']})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_REPLACE, [])})
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertFalse('title' in self.connection_2.strategy.entries[dn])

    def test_modify_replace_existing_novalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn', 'title': ['title1', 'title3']})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_REPLACE, [])})
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertFalse('title' in self.connection_3.strategy.entries[dn])

    def test_modify_replace_not_existing_novalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_REPLACE, [])})
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertFalse('title' in self.connection_1.strategy.entries[dn])

    def test_modify_replace_not_existing_novalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_REPLACE, [])})
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertFalse('title' in self.connection_2.strategy.entries[dn])

    def test_modify_replace_not_existing_novalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_REPLACE, [])})
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertFalse('title' in self.connection_3.strategy.entries[dn])

    def test_modify_replace_not_existing_singlevalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_REPLACE, ['title1'])})
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertTrue('title1' in self.connection_1.strategy.entries[dn]['title'])

    def test_modify_replace_not_existing_singlevalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_REPLACE, ['title1'])})
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertTrue('title1' in self.connection_2.strategy.entries[dn]['title'])

    def test_modify_replace_not_existing_singlevalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_REPLACE, ['title1'])})
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertTrue('title1' in self.connection_3.strategy.entries[dn]['title'])

    def test_modify_replace_not_existing_multivalue_1(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1.modify(dn, {'title': (MODIFY_REPLACE, ['title1', 'title2'])})
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertTrue('title1' in self.connection_1.strategy.entries[dn]['title'])
        self.assertTrue('title2' in self.connection_1.strategy.entries[dn]['title'])

    def test_modify_replace_not_existing_multivalue_2(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2.modify(dn, {'title': (MODIFY_REPLACE, ['title1', 'title2'])})
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertTrue('title1' in self.connection_2.strategy.entries[dn]['title'])
        self.assertTrue('title2' in self.connection_2.strategy.entries[dn]['title'])

    def test_modify_replace_not_existing_multivalue_3(self):
        dn = 'cn=user_test,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.add(dn, 'inetOrgPerson', attributes={'givenname': 'user_test', 'sn': 'user_test_sn'})
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3.modify(dn, {'title': (MODIFY_REPLACE, ['title1', 'title3'])})
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertTrue('title1' in self.connection_3.strategy.entries[dn]['title'])
        self.assertTrue('title3' in self.connection_3.strategy.entries[dn]['title'])

    def test_search_exact_match_single_attribute_1(self):
        self.connection_1.bind()
        self.connection_1.search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        self.assertEqual(self.connection_1.result['description'], 'success')
        self.assertEqual('user0', self.connection_1.response[0]['attributes']['cn'][0])

    def test_search_exact_match_single_attribute_2(self):
        self.connection_2.bind()
        self.connection_2.search('o=lab', '(cn=user2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        self.assertEqual(self.connection_2.result['description'], 'success')
        self.assertEqual('admin', self.connection_2.response[0]['attributes']['cn'][0])

    def test_search_exact_match_single_attribute_3(self):
        self.connection_3.bind()
        self.connection_3.search('o=lab', '(cn=user3)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        self.assertEqual(self.connection_3.result['description'], 'success')
        self.assertEqual('admin', self.connection_3.response[0]['attributes']['cn'][0])
