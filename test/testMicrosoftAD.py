# Created on 2013.06.06
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
from time import sleep

from ldap3 import SUBTREE
from ldap3.protocol.microsoft import extended_dn_control, show_deleted_control, dir_sync_control
from test import test_base, test_name_attr, random_id, get_connection, \
    add_user, drop_connection, test_server_type, test_root_partition

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection()
        self.delete_at_teardown = []
        if test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-1', attributes={'givenName': 'givenname-1'}))
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'search-2', attributes={'givenName': 'givenname-2'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_extended_dn_ad(self):
        if test_server_type == 'AD':
            result = self.connection.search(search_base=test_base, search_filter='(' + test_name_attr + '=' + testcase_id + 'search-1)', attributes=[test_name_attr], controls=[extended_dn_control(), show_deleted_control()])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
                result = self.connection.result

            self.assertEqual(result['description'], 'success')
            self.assertTrue('<GUID=' in response[0]['dn'])
            self.assertTrue('SID=' in response[0]['dn'])
            self.assertTrue('>;' in response[0]['dn'])

    def test_search_deleted_objects_ad(self):
        if test_server_type == 'AD':
            dn_to_delete, _ = add_user(self.connection, testcase_id, 'to-be-deleted-1', attributes={'givenName': 'to-be-deleted-1'})
            sleep(1)
            self.connection.delete(dn_to_delete)
            sleep(1)
            result = self.connection.search(search_base=test_root_partition,
                                            search_filter='(&(isDeleted=TRUE)(cn=*' + testcase_id + '*deleted-1*))',
                                            search_scope=SUBTREE,
                                            attributes=[],
                                            controls=[show_deleted_control(criticality=True)])
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
                result = self.connection.result
            found = False
            for entry in response:
                if entry['type'] == 'searchResEntry' and testcase_id in entry['dn']:
                    found = True
                    break

            self.assertTrue(found)

    def test_dir_sync(self):
        if test_server_type == 'AD':
            sync = self.connection.extend.microsoft.dir_sync(test_root_partition, max_length=16384)
            sync_data = sync.loop()
            print(sync_data)
