"""
"""

# Created on 2015.02.3
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

from ldap3 import Server, Connection, MOCK_SYNC, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, OFFLINE_EDIR_9_1_4,\
    BASE, LEVEL, SUBTREE, AUTO_BIND_NO_TLS, NONE
from ldap3.core.exceptions import LDAPInvalidCredentialsResult, LDAPNoSuchObjectResult
from ldap3.protocol.rfc4512 import SchemaInfo, DsaInfo
from ldap3.protocol.schemas.edir914 import edir_9_1_4_dsa_info, edir_9_1_4_schema
from test.config import random_id

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        # The mock server can be defined in two different ways, so tests are duplicated, connection_3 is without schema
        schema = SchemaInfo.from_json(edir_9_1_4_schema)
        info = DsaInfo.from_json(edir_9_1_4_dsa_info, schema)
        server_1 = Server.from_definition('MockSyncServer', info, schema)
        self.connection_1 = Connection(server_1, user='cn=user1,ou=test,o=lab', password='test1111', client_strategy=MOCK_SYNC)
        self.connection_1b = Connection(server_1, user='cn=user1,ou=test,o=lab', password='test1111', client_strategy=MOCK_SYNC)
        self.connection_1c = Connection(server_1, user='cn=user1,ou=test,o=lab', password='test1111', client_strategy=MOCK_SYNC, raise_exceptions=True)
        server_2 = Server('dummy', get_info=OFFLINE_EDIR_9_1_4)
        self.connection_2 = Connection(server_2, user='cn=user2,ou=test,o=lab', password='test2222', client_strategy=MOCK_SYNC)
        self.connection_2b = Connection(server_2, user='cn=user2,ou=test,o=lab', password='test2222', client_strategy=MOCK_SYNC)
        self.connection_2c = Connection(server_2, user='cn=user2,ou=test,o=lab', password='test2222', client_strategy=MOCK_SYNC, raise_exceptions=True)
        server_3 = Server('dummy')  # no schema
        self.connection_3 = Connection(server_3, user='cn=user3,ou=test,o=lab', password='test3333', client_strategy=MOCK_SYNC)
        self.connection_3b = Connection(server_3, user='cn=user3,ou=test,o=lab', password='test3333', client_strategy=MOCK_SYNC)
        self.connection_3c = Connection(server_3, user='cn=user3,ou=test,o=lab', password='test3333', client_strategy=MOCK_SYNC, raise_exceptions=True)
        # creates fixtures
        self.connection_1.strategy.add_entry('cn=user0,o=lab', {'userPassword': 'test0000', 'sn': 'user0_sn', 'revision': 0, 'guid': '07039e68-4373-264d-a0a7-000000000000'})
        self.connection_2.strategy.add_entry('cn=user0,o=lab', {'userPassword': 'test0000', 'sn': 'user0_sn', 'revision': 0, 'guid': '07039e68-4373-264d-a0a7-000000000000'})
        self.connection_3.strategy.add_entry('cn=user0,o=lab', {'userPassword': 'test0000', 'sn': 'user0_sn', 'revision': 0, 'guid': '07039e68-4373-264d-a0a7-000000000000'})
        self.connection_1.strategy.add_entry('cn=user1,ou=test,o=lab', {'userPassword': 'test1111', 'sn': 'user1_sn', 'revision': 1, 'guid': '07039e68-4373-264d-a0a7-111111111111'})
        self.connection_2.strategy.add_entry('cn=user1,ou=test,o=lab', {'userPassword': 'test1111', 'sn': 'user1_sn', 'revision': 1, 'guid': '07039e68-4373-264d-a0a7-111111111111'})
        self.connection_3.strategy.add_entry('cn=user1,ou=test,o=lab', {'userPassword': 'test1111', 'sn': 'user1_sn', 'revision': 1, 'guid': '07039e68-4373-264d-a0a7-111111111111'})
        self.connection_1.strategy.add_entry('cn=user2,ou=test,o=lab', {'userPassword': 'test2222', 'sn': 'user2_sn', 'revision': 2, 'guid': '07039e68-4373-264d-a0a7-222222222222'})
        self.connection_2.strategy.add_entry('cn=user2,ou=test,o=lab', {'userPassword': 'test2222', 'sn': 'user2_sn', 'revision': 2, 'guid': '07039e68-4373-264d-a0a7-222222222222'})
        self.connection_3.strategy.add_entry('cn=user2,ou=test,o=lab', {'userPassword': 'test2222', 'sn': 'user2_sn', 'revision': 2, 'guid': '07039e68-4373-264d-a0a7-222222222222'})
        self.connection_1.strategy.add_entry('cn=user3,ou=test,o=lab', {'userPassword': 'test3333', 'sn': 'user3_sn', 'revision': 3, 'guid': '07039e68-4373-264d-a0a7-333333333333'})
        self.connection_2.strategy.add_entry('cn=user3,ou=test,o=lab', {'userPassword': 'test3333', 'sn': 'user3_sn', 'revision': 3, 'guid': '07039e68-4373-264d-a0a7-333333333333'})
        self.connection_3.strategy.add_entry('cn=user3,ou=test,o=lab', {'userPassword': 'test3333', 'sn': 'user3_sn', 'revision': 3, 'guid': '07039e68-4373-264d-a0a7-333333333333'})
        self.connection_1.strategy.add_entry('cn=user4,ou=test,o=lab', {'userPassword': 'test4444', 'sn': 'user4_sn', 'revision': 4, 'title': ['title1', 'title2', 'title3'], 'guid': '07039e68-4373-264d-a0a7-444444444444'})
        self.connection_2.strategy.add_entry('cn=user4,ou=test,o=lab', {'userPassword': 'test4444', 'sn': 'user4_sn', 'revision': 4, 'title': ['title1', 'title2', 'title3'], 'guid': '07039e68-4373-264d-a0a7-444444444444'})
        self.connection_3.strategy.add_entry('cn=user4,ou=test,o=lab', {'userPassword': 'test4444', 'sn': 'user4_sn', 'revision': 4, 'title': ['title1', 'title2', 'title3'], 'guid': '07039e68-4373-264d-a0a7-444444444444'})

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

    def test_invalid_bind_1(self):
        self.connection_1.password = 'wrong'
        self.connection_1.open()
        self.connection_1.bind()
        self.assertFalse(self.connection_1.bound)

    def test_invalid_bind_2(self):
        self.connection_2.password = 'wrong'
        self.connection_2.open()
        self.connection_2.bind()
        self.assertFalse(self.connection_2.bound)

    def test_invalid_bind_3(self):
        self.connection_3.password = 'wrong'
        self.connection_3.open()
        self.connection_3.bind()
        self.assertFalse(self.connection_3.bound)

    def test_invalid_bind_exception_1(self):
        self.connection_1c.password = 'wrong'
        self.connection_1c.open()
        try:
            self.connection_1c.bind()
            self.fail('exception not raised')
        except LDAPInvalidCredentialsResult:
            pass

    def test_invalid_bind_exception_2(self):
        self.connection_2c.password = 'wrong'
        self.connection_2c.open()
        try:
            self.connection_2c.bind()
            self.fail('exception not raised')
        except LDAPInvalidCredentialsResult:
            pass

    def test_invalid_bind_exception_3(self):
        self.connection_3c.password = 'wrong'
        self.connection_3c.open()
        try:
            self.connection_3c.bind()
            self.fail('exception not raised')
        except LDAPInvalidCredentialsResult:
            pass

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
        self.assertFalse(self.connection_2.bound)

    def test_remove_user_3(self):
        self.connection_3.strategy.remove_entry('cn=user1,ou=test,o=lab')
        self.connection_3.bind()
        self.assertTrue(self.connection_3.bound)
        self.connection_3.rebind('cn=user1,ou=test,o=lab', 'test1111')
        self.assertFalse(self.connection_3.bound)

    def test_delete_1(self):
        self.connection_1.bind()
        result = self.connection_1.delete('cn=user1,ou=test,o=lab')
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result

        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user1,ou=test,o=lab' not in self.connection_1.strategy.entries)

    def test_delete_2(self):
        self.connection_2.bind()
        result = self.connection_2.delete('cn=user2,ou=test,o=lab')
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(['description'], 'success')
        self.assertTrue('cn=user2,ou=test,o=lab' not in self.connection_2.strategy.entries)

    def test_delete_3(self):
        self.connection_3.bind()
        result = self.connection_3.delete('cn=user3,ou=test,o=lab')
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user3,ou=test,o=lab' not in self.connection_3.strategy.entries)

    def test_add_entry_1(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.add(dn, ['inetOrgPerson', 'top'], {'sn': 'user5_sn'})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(dn in self.connection_1.strategy.entries)
        self.connection_1b.bind()
        self.assertTrue(dn in self.connection_1b.strategy.entries)

    def test_add_entry_2(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.add(dn, ['inetOrgPerson', 'top'], {'sn': 'user5_sn'})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(dn in self.connection_2.strategy.entries)
        self.connection_2b.bind()
        self.assertTrue(dn in self.connection_2b.strategy.entries)

    def test_add_entry_3(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.add(dn, ['inetOrgPerson', 'top'], {'sn': 'user5_sn'})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(dn in self.connection_3.strategy.entries)
        self.connection_3b.bind()
        self.assertTrue(dn in self.connection_3b.strategy.entries)

    def test_add_entry_already_exists_1(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_1.bind()
        self.connection_1.strategy.add_entry(dn, {'objectClass': ['inetOrgPerson', 'top'], 'sn': 'user5_sn'})
        result = self.connection_1.add(dn, ['inetOrgPerson', 'top'], {'sn': 'user5_sn'})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'entryAlreadyExists')

    def test_add_entry_already_exists_2(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_2.bind()
        self.connection_2.strategy.add_entry(dn, {'objectClass': ['inetOrgPerson', 'top'], 'sn': 'user5_sn'})
        result = self.connection_2.add(dn, ['inetOrgPerson', 'top'], {'sn': 'user5_sn'})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'entryAlreadyExists')

    def test_add_entry_already_exists_3(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_3.bind()
        self.connection_3.strategy.add_entry(dn, {'objectClass': ['inetOrgPerson', 'top'], 'sn': 'user5_sn'})
        result = self.connection_3.add(dn, ['inetOrgPerson', 'top'], {'sn': 'user5_sn'})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'entryAlreadyExists')

    def test_delete_entry_nonexisting_1(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_1.bind()
        self.assertTrue(dn not in self.connection_1.strategy.entries)
        result = self.connection_1.delete(dn)
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_delete_entry_nonexisting_2(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_2.bind()
        self.assertTrue(dn not in self.connection_2.strategy.entries)
        result = self.connection_2.delete(dn)
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_delete_entry_nonexisting_3(self):
        dn = 'cn=user5,ou=test,o=lab'
        self.connection_3.bind()
        self.assertTrue(dn not in self.connection_3.strategy.entries)
        result = self.connection_3.delete(dn)
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_compare_entry_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.compare(dn, 'sn', 'user4_sn')
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'compareTrue')
        result = self.connection_1.compare(dn, 'sn', 'bad_sn')
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'compareFalse')

    def test_compare_entry_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.compare(dn, 'sn', 'user4_sn')
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'compareTrue')
        result = self.connection_2.compare(dn, 'sn', 'bad_sn')
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'compareFalse')

    def test_compare_entry_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.compare(dn, 'sn', 'user4_sn')
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'compareTrue')
        result = self.connection_3.compare(dn, 'sn', 'bad_sn')
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'compareFalse')

    def test_move_dn_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify_dn(dn, relative_dn='cn=user4', new_superior='ou=moved,o=lab')
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user4,ou=moved,o=lab' in self.connection_1.strategy.entries)
        self.assertFalse(dn in self.connection_1.strategy.entries)

    def test_move_dn_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify_dn(dn, relative_dn='cn=user4', new_superior='ou=moved,o=lab')
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user4,ou=moved,o=lab' in self.connection_2.strategy.entries)
        self.assertFalse(dn in self.connection_2.strategy.entries)

    def test_move_dn_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify_dn(dn, relative_dn='cn=user4', new_superior='ou=moved,o=lab')
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user4,ou=moved,o=lab' in self.connection_3.strategy.entries)
        self.assertFalse(dn in self.connection_3.strategy.entries)

    def test_rename_dn_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify_dn(dn, relative_dn='cn=user_renamed')
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user_renamed,ou=test,o=lab' in self.connection_1.strategy.entries)
        self.assertFalse(dn in self.connection_1.strategy.entries)

    def test_rename_dn_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify_dn(dn, relative_dn='cn=user_renamed')
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user_renamed,ou=test,o=lab' in self.connection_2.strategy.entries)
        self.assertFalse(dn in self.connection_2.strategy.entries)

    def test_rename_dn_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify_dn(dn, relative_dn='cn=user_renamed')
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue('cn=user_renamed,ou=test,o=lab' in self.connection_3.strategy.entries)
        self.assertFalse(dn in self.connection_3.strategy.entries)

    def test_modify_add_existing_singlevalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'sn': (MODIFY_ADD, ['sn_added'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'sn_added' in self.connection_1.strategy.entries[dn]['sn'])

    def test_modify_add_existing_singlevalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'sn': (MODIFY_ADD, ['sn_added'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'sn_added' in self.connection_2.strategy.entries[dn]['sn'])

    def test_modify_add_existing_singlevalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'sn': (MODIFY_ADD, ['sn_added'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'sn_added' in self.connection_3.strategy.entries[dn]['sn'])

    def test_modify_add_nonexisting_singlevalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'title': (MODIFY_ADD, ['title_added'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'title_added' in self.connection_1.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_singlevalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'title': (MODIFY_ADD, ['title_added'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'title_added' in self.connection_2.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_singlevalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'title': (MODIFY_ADD, ['title_added'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'title_added' in self.connection_3.strategy.entries[dn]['title'])

    def test_modify_add_existing_multivalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'sn': (MODIFY_ADD, ['sn_added1', 'sn_added2'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'sn_added1' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertTrue(b'sn_added2' in self.connection_1.strategy.entries[dn]['sn'])

    def test_modify_add_existing_multivalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'sn': (MODIFY_ADD, ['sn_added1', 'sn_added2'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'sn_added1' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertTrue(b'sn_added2' in self.connection_2.strategy.entries[dn]['sn'])

    def test_modify_add_existing_multivalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'sn': (MODIFY_ADD, ['sn_added1', 'sn_added2'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'sn_added1' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertTrue(b'sn_added2' in self.connection_3.strategy.entries[dn]['sn'])

    def test_modify_add_nonexisting_multivalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'title': (MODIFY_ADD, ['title_added1', 'title_added2'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'title_added1' in self.connection_1.strategy.entries[dn]['title'])
        self.assertTrue(b'title_added2' in self.connection_1.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_multivalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'title': (MODIFY_ADD, ['title_added1', 'title_added2'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'title_added1' in self.connection_2.strategy.entries[dn]['title'])
        self.assertTrue(b'title_added2' in self.connection_2.strategy.entries[dn]['title'])

    def test_modify_add_nonexisting_multivalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'title': (MODIFY_ADD, ['title_added1', 'title_added2'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertTrue(result['description'], 'success')
        self.assertTrue(b'title_added1' in self.connection_3.strategy.entries[dn]['title'])
        self.assertTrue(b'title_added2' in self.connection_3.strategy.entries[dn]['title'])

    def test_modify_delete_nonexisting_attribute_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'initials': (MODIFY_DELETE, ['initials1', 'initials2'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'noSuchAttribute')

    def test_modify_delete_nonexisting_attribute_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'initials': (MODIFY_DELETE, ['initials1', 'initials2'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'noSuchAttribute')

    def test_modify_delete_nonexisting_attribute_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'initials': (MODIFY_DELETE, ['initials1', 'initials2'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'noSuchAttribute')

    def test_modify_delete_existing_singlevalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'title': (MODIFY_DELETE, ['title1'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')

    def test_modify_delete_existing_singlevalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'sn': (MODIFY_DELETE, ['user4_sn'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')

    def test_modify_delete_existing_singlevalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'sn': (MODIFY_DELETE, ['user4_sn'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')

    def test_modify_delete_existing_multivalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'title': (MODIFY_DELETE, ['title1', 'title2'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(self.connection_1.strategy.entries[dn]['title'] == [b'title3'])

    def test_modify_delete_existing_multivalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'title': (MODIFY_DELETE, ['title1', 'title2'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(self.connection_2.strategy.entries[dn]['title'] == [b'title3'])

    def test_modify_delete_existing_multivalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'title': (MODIFY_DELETE, ['title1', 'title2'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(self.connection_3.strategy.entries[dn]['title'] == [b'title3'])

    def test_modify_replace_existing_singlevalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'user_test_sn' in self.connection_1.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_1.strategy.entries[dn]['sn']), 1)

    def test_modify_replace_existing_singlevalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'user_test_sn' in self.connection_2.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_2.strategy.entries[dn]['sn']), 1)

    def test_modify_replace_existing_singlevalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'sn': (MODIFY_REPLACE, ['user_test_sn'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'user_test_sn' in self.connection_3.strategy.entries[dn]['sn'])
        self.assertEqual(len(self.connection_3.strategy.entries[dn]['sn']), 1)

    def test_modify_replace_existing_multivalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'title': (MODIFY_REPLACE, ['title4', 'title5'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'title1' in self.connection_1.strategy.entries[dn]['title'])
        self.assertFalse(b'title2' in self.connection_1.strategy.entries[dn]['title'])
        self.assertFalse(b'title3' in self.connection_1.strategy.entries[dn]['title'])
        self.assertTrue(b'title4' in self.connection_1.strategy.entries[dn]['title'])
        self.assertTrue(b'title5' in self.connection_1.strategy.entries[dn]['title'])
        self.assertEqual(len(self.connection_1.strategy.entries[dn]['title']), 2)

    def test_modify_replace_existing_multivalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'title': (MODIFY_REPLACE, ['title4', 'title5'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'title1' in self.connection_2.strategy.entries[dn]['title'])
        self.assertFalse(b'title2' in self.connection_2.strategy.entries[dn]['title'])
        self.assertFalse(b'title3' in self.connection_2.strategy.entries[dn]['title'])
        self.assertTrue(b'title4' in self.connection_2.strategy.entries[dn]['title'])
        self.assertTrue(b'title5' in self.connection_2.strategy.entries[dn]['title'])
        self.assertEqual(len(self.connection_2.strategy.entries[dn]['title']), 2)

    def test_modify_replace_existing_multivalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'title': (MODIFY_REPLACE, ['title4', 'title5'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'title1' in self.connection_3.strategy.entries[dn]['title'])
        self.assertFalse(b'title2' in self.connection_3.strategy.entries[dn]['title'])
        self.assertFalse(b'title3' in self.connection_3.strategy.entries[dn]['title'])
        self.assertTrue(b'title4' in self.connection_3.strategy.entries[dn]['title'])
        self.assertTrue(b'title5' in self.connection_3.strategy.entries[dn]['title'])
        self.assertEqual(len(self.connection_3.strategy.entries[dn]['title']), 2)

    def test_modify_replace_existing_novalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'title': (MODIFY_REPLACE, [])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'title' in self.connection_1.strategy.entries[dn])

    def test_modify_replace_existing_novalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'title': (MODIFY_REPLACE, [])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'title' in self.connection_2.strategy.entries[dn])

    def test_modify_replace_existing_novalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'title': (MODIFY_REPLACE, [])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'title' in self.connection_3.strategy.entries[dn])

    def test_modify_replace_not_existing_novalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'initials': (MODIFY_REPLACE, [])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'initials' in self.connection_1.strategy.entries[dn])

    def test_modify_replace_not_existing_novalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'initials': (MODIFY_REPLACE, [])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'initials' in self.connection_2.strategy.entries[dn])

    def test_modify_replace_not_existing_novalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'initials': (MODIFY_REPLACE, [])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertFalse(b'initials' in self.connection_3.strategy.entries[dn])

    def test_modify_replace_not_existing_singlevalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'initials': (MODIFY_REPLACE, ['initials1'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'initials1' in self.connection_1.strategy.entries[dn]['initials'])

    def test_modify_replace_not_existing_singlevalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'initials': (MODIFY_REPLACE, ['initials1'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'initials1' in self.connection_2.strategy.entries[dn]['initials'])

    def test_modify_replace_not_existing_singlevalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'initials': (MODIFY_REPLACE, ['initials1'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'initials1' in self.connection_3.strategy.entries[dn]['initials'])

    def test_modify_replace_not_existing_multivalue_1(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_1.bind()
        result = self.connection_1.modify(dn, {'initials': (MODIFY_REPLACE, ['initials1', 'initials2'])})
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'initials1' in self.connection_1.strategy.entries[dn]['initials'])
        self.assertTrue(b'initials2' in self.connection_1.strategy.entries[dn]['initials'])

    def test_modify_replace_not_existing_multivalue_2(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_2.bind()
        result = self.connection_2.modify(dn, {'initials': (MODIFY_REPLACE, ['initials1', 'initials2'])})
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'initials1' in self.connection_2.strategy.entries[dn]['initials'])
        self.assertTrue(b'initials2' in self.connection_2.strategy.entries[dn]['initials'])

    def test_modify_replace_not_existing_multivalue_3(self):
        dn = 'cn=user4,ou=test,o=lab'
        self.connection_3.bind()
        result = self.connection_3.modify(dn, {'initials': (MODIFY_REPLACE, ['initials1', 'initials2'])})
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(b'initials1' in self.connection_3.strategy.entries[dn]['initials'])
        self.assertTrue(b'initials2' in self.connection_3.strategy.entries[dn]['initials'])

    def test_search_exact_match_single_attribute_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(cn=user1)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user1', response[0]['attributes']['cn'][0])

    def test_search_exact_match_single_attribute_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(cn=user2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user2', response[0]['attributes']['cn'][0])

    def test_search_exact_match_single_attribute_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(cn=user3)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user3', response[0]['attributes']['cn'][0])

    def test_search_exact_match_single_binary_attribute_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(guid=07039e68-4373-264d-a0a7-111111111111)', search_scope=SUBTREE, attributes=['cn', 'guid'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user1', response[0]['attributes']['cn'][0])
        self.assertEqual('07039e68-4373-264d-a0a7-111111111111', response[0]['attributes']['guid'])

    def test_search_exact_match_single_binary_attribute_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(guid=07039e68-4373-264d-a0a7-222222222222)', search_scope=SUBTREE, attributes=['cn', 'guid'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user2', response[0]['attributes']['cn'][0])
        self.assertEqual('07039e68-4373-264d-a0a7-222222222222', response[0]['attributes']['guid'])

    def test_search_exact_match_single_binary_attribute_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(guid=07039e68-4373-264d-a0a7-333333333333)', search_scope=SUBTREE, attributes=['cn', 'guid'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user3', response[0]['attributes']['cn'][0])
        self.assertEqual('07039e68-4373-264d-a0a7-333333333333', response[0]['attributes']['guid'][0])

    def test_search_exact_match_case_insensitive_single_attribute_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(cn=UsEr1)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user1', response[0]['attributes']['cn'][0])

    def test_search_exact_match_case_insensitive_single_attribute_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(cn=UsEr2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user2', response[0]['attributes']['cn'][0])

    def test_search_exact_match_case_insensitive_single_attribute_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(cn=UsEr3)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual('user3', response[0]['attributes']['cn'][0])

    def test_search_presence_single_attribute_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue('user' in response[0]['attributes']['cn'][0])

    def test_search_presence_single_attribute_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue('user' in response[0]['attributes']['cn'][0])

    def test_search_presence_single_attribute_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue('user' in response[0]['attributes']['cn'][0])

    def test_search_presence_and_filter_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(&(cn=*)(|(sn=user0_sn)(sn=user1_sn)))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1'])

        self.connection_1b.bind()
        result = self.connection_1b.search('o=lab', '(&(cn=*)(|(sn=user0_sn)(sn=user1_sn)))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1b.response
        if not self.connection_1b.strategy.sync:
            response, result = self.connection_1b.get_response(result)
        else:
            result = self.connection_1b.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1'])

    def test_search_presence_and_filter_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(&(cn=*)(|(sn=user0_sn)(sn=user1_sn)))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1'])

        self.connection_2b.bind()
        result = self.connection_2b.search('o=lab', '(&(cn=*)(|(sn=user0_sn)(sn=user1_sn)))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2b.response
        if not self.connection_2b.strategy.sync:
            response, result = self.connection_2b.get_response(result)
        else:
            result = self.connection_2b.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1'])

    def test_search_presence_and_filter_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(&(cn=*)(|(sn=user0_sn)(sn=user1_sn)))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1'])

        self.connection_3b.bind()
        result = self.connection_3b.search('o=lab', '(&(cn=*)(|(sn=user0_sn)(sn=user1_sn)))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3b.response
        if not self.connection_3b.strategy.sync:
            response, result = self.connection_3b.get_response(result)
        else:
            result = self.connection_3b.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1'])

    def test_search_incorrect_base_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=nonexistant', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        if not self.connection_1.strategy.sync:
            _, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_search_incorrect_base_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=nonexistant', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        if not self.connection_2.strategy.sync:
            _, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_search_incorrect_base_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=nonexistant', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        if not self.connection_3.strategy.sync:
            _, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_search_incorrect_base_exception_1(self):
        self.connection_1c.bind()
        try:
            result = self.connection_1c.search('o=nonexistant', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
            self.fail('exception not raised')
        except LDAPNoSuchObjectResult:
            pass

        if not self.connection_1c.strategy.sync:
            _, result = self.connection_1c.get_response(result)
        else:
            result = self.connection_1c.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_search_incorrect_base_exception_2(self):
        self.connection_2c.bind()
        try:
            result = self.connection_2c.search('o=nonexistant', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
            self.fail('exception not raised')
        except LDAPNoSuchObjectResult:
            pass

        if not self.connection_2c.strategy.sync:
            _, result = self.connection_2c.get_response(result)
        else:
            result = self.connection_2c.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_search_incorrect_base_exception_3(self):
        self.connection_3c.bind()
        try:
            result = self.connection_3c.search('o=nonexistant', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'sn'])
            self.fail('exception not raised')
        except LDAPNoSuchObjectResult:
            pass

        if not self.connection_3c.strategy.sync:
            _, result = self.connection_3c.get_response(result)
        else:
            result = self.connection_3c.result
        self.assertEqual(result['description'], 'noSuchObject')

    def test_search_presence_and_filter_no_entries_found_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(&(cn=*)(sn=user_nonexistant))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 0)

    def test_search_presence_and_filter_no_entries_found_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(&(cn=*)(sn=user_nonexistant))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 0)

    def test_search_presence_and_filter_no_entries_found_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(&(cn=*)(sn=user_nonexistant))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertEqual(len(response), 0)

    def test_search_exact_match_not_filter_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(!(sn=user0_sn))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertNotEqual(response[0]['attributes']['cn'][0], 'user0')

    def test_search_exact_match_not_filter_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(!(sn=user0_sn))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertNotEqual(response[0]['attributes']['cn'][0], 'user0')

    def test_search_exact_match_not_filter_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(!(sn=user0_sn))', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertNotEqual(response[0]['attributes']['cn'][0], 'user0')

    def test_search_greater_or_equal_than_string_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(userPassword>=test2222)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2', 'user3', 'user4'])

    def test_search_greater_or_equal_than_string_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(userPassword>=test2222)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2', 'user3', 'user4'])

    def test_search_greater_or_equal_than_string_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(userPassword>=test2222)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2', 'user3', 'user4'])

    def test_search_greater_or_equal_than_int_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(revision>=2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2', 'user3', 'user4'])

    def test_search_greater_or_equal_than_int_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(revision>=2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2', 'user3', 'user4'])

    def test_search_greater_or_equal_than_int_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(revision>=2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2', 'user3', 'user4'])

    def test_search_less_or_equal_than_string_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(userPassword<=test2222)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1', 'user2'])

    def test_search_less_or_equal_than_string_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(userPassword<=test2222)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1', 'user2'])

    def test_search_less_or_equal_than_string_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(userPassword<=test2222)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1', 'user2'])

    def test_search_less_or_equal_than_int_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(revision<=2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1', 'user2'])

    def test_search_less_or_equal_than_int_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(revision<=2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1', 'user2'])

    def test_search_less_or_equal_than_int_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(revision<=2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user0', 'user1', 'user2'])

    def test_search_substring_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(cn=*ser*2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2'])

    def test_search_substring_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(cn=*ser*2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2'])

    def test_search_substring_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(cn=*ser*2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2'])

    def test_search_case_insensitive_substring_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(cn=*SeR*2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2'])

    def test_search_case_insensitive_substring_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(cn=*SeR*2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2'])

    def test_search_case_insensitive_substring_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(cn=*SeR*2)', search_scope=SUBTREE, attributes=['cn', 'sn'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(response[0]['attributes']['cn'][0] in ['user2'])

    def test_search_presence_singlevalue_attribute_1(self):
        self.connection_1.bind()
        result = self.connection_1.search('o=lab', '(revision=*)', search_scope=SUBTREE, attributes=['cn', 'revision'])
        response = self.connection_1.response
        if not self.connection_1.strategy.sync:
            response, result = self.connection_1.get_response(result)
        else:
            result = self.connection_1.result
        self.assertEqual(result['description'], 'success')

        self.assertTrue(isinstance(response[0]['attributes']['revision'], int))

    def test_search_presence_singlevalue_attribute_2(self):
        self.connection_2.bind()
        result = self.connection_2.search('o=lab', '(revision=*)', search_scope=SUBTREE, attributes=['cn', 'revision'])
        response = self.connection_2.response
        if not self.connection_2.strategy.sync:
            response, result = self.connection_2.get_response(result)
        else:
            result = self.connection_2.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(isinstance(response[0]['attributes']['revision'], int))

    def test_search_presence_singlevalue_attribute_3(self):
        self.connection_3.bind()
        result = self.connection_3.search('o=lab', '(revision=*)', search_scope=SUBTREE, attributes=['cn', 'revision'])
        response = self.connection_3.response
        if not self.connection_3.strategy.sync:
            response, result = self.connection_3.get_response(result)
        else:
            result = self.connection_3.result
        self.assertEqual(result['description'], 'success')
        self.assertTrue(isinstance(response[0]['attributes']['revision'], list))  # no schema so attributes are returned as lists

    def test_search_paged_1(self):
        self.connection_1.bind()
        response = []
        for resp in self.connection_1.extend.standard.paged_search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'revision'], paged_size=2, paged_criticality=True):
            response.append(resp)

        self.assertEqual(len(response), 5)

    def test_search_paged_2(self):
        self.connection_2.bind()
        response = []
        for resp in self.connection_2.extend.standard.paged_search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'revision'], paged_size=2, paged_criticality=True):
            response.append(resp)

        self.assertEqual(len(response), 5)

    def test_search_paged_3(self):
        self.connection_3.bind()
        response = []
        for resp in self.connection_3.extend.standard.paged_search('o=lab', '(cn=*)', search_scope=SUBTREE, attributes=['cn', 'revision'], paged_size=2, paged_criticality=True):
            response.append(resp)

        self.assertEqual(len(response), 5)
