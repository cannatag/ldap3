# Created on 2014.06.30
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

from ldap3 import LDAPExtensionError
from test import test_user, test_server_context, test_server_edir_name, random_id, get_connection, drop_connection, add_user, test_server_type, \
    test_name_attr, test_base, test_password


testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(check_names=True)
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-3'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-4'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-5'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-6'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-7'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'paged_search-8'))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_who_am_i_extension(self):
        if not test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            try:
                if not self.connection.server.info:
                    self.connection.refresh_server_info()
                self.connection.extend.standard.who_am_i()
                result = self.connection.result
                self.assertEqual(result['description'], 'success')
            except LDAPExtensionError as e:
                if not e.args[0] == 'extension not in DSA list of supported extensions':
                    raise

    def test_get_bind_dn_extension(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            result = self.connection.extend.novell.get_bind_dn()
            self.assertTrue(test_user in result)

    def test_paged_search_accumulator(self):
        if not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            responses = self.connection.extend.standard.paged_search(test_base, '(' + test_name_attr + '=' + testcase_id + 'paged_search-*)', generator=False, paged_size=3)
            self.assertEqual(len(responses), 8)

    def test_paged_search_generator(self):
        if not self.connection.strategy.pooled and not self.connection.strategy.no_real_dsa:
            responses = []
            for response in self.connection.extend.standard.paged_search(test_base, '(' + test_name_attr + '=' + testcase_id + 'paged_search-*)'):
                responses.append(response)
            self.assertEqual(len(responses), 8)

    def test_novell_list_replicas(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.extend.novell.list_replicas('cn=' + test_server_edir_name + ',' + test_server_context)
            self.assertEqual(result, None)

    def test_novell_replica_info(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.extend.novell.replica_info('cn=' + test_server_edir_name + ',' + test_server_context, '')
            self.assertEqual(result, '')

    def test_novell_partition_entry_count(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            result = self.connection.extend.novell.partition_entry_count(test_base)
            self.assertTrue(result > 0)

    def test_novell_get_universal_password(self):
        if test_server_type == 'EDIR' and not self.connection.strategy.no_real_dsa:
            self.connection.start_tls()
            result = self.connection.extend.novell.get_universal_password(test_user)
            self.assertTrue(result, test_password)
