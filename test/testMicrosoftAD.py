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

from ldap3 import SUBTREE, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SIMPLE
from ldap3.protocol.microsoft import extended_dn_control, show_deleted_control
from test import test_base, test_name_attr, random_id, get_connection, add_user, drop_connection, test_server_type, test_root_partition

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(use_ssl=True)
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
            sync = self.connection.extend.microsoft.dir_sync(test_root_partition, attributes=['*'])
            # read all previous changes
            while sync.more_results:
                print('PREV', len(sync.loop()))

            # add a new object and verify the sync
            dn, _ = add_user(self.connection, testcase_id, 'to-be-deleted-1', attributes={'givenName': 'to-be-deleted-1'})
            sleep(1)
            response = sync.loop()
            print('ADD OBJ', len(response), response[0]['attributes'])
            found = False
            for entry in response:
                if entry['type'] == 'searchResEntry' and testcase_id + 'to-be-deleted-1' in entry['dn']:
                    found = True
                    break
            self.assertTrue(found)

            # modify-add an attribute and verify the sync
            result = self.connection.modify(dn, {'businessCategory': (MODIFY_ADD, ['businessCategory-1-added'])})
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')
            sleep(1)
            response = sync.loop()
            print('MOD-ADD ATTR', len(response), response[0]['attributes'])
            found = False
            for entry in response:
                if entry['type'] == 'searchResEntry' and testcase_id + 'to-be-deleted-1' in entry['dn']:
                    found = True
                    break
            self.assertTrue(found)

            # modify-replace an attribute and verify the sync
            result = self.connection.modify(dn, {'businessCategory': (MODIFY_REPLACE, ['businessCategory-1-replaced']), 'sn': (MODIFY_REPLACE, ['sn-replaced'])})
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')
            sleep(1)
            response = sync.loop()
            print('MOD-REPLACE ATTR', len(response), response[0]['attributes'])
            found = False
            for entry in response:
                if entry['type'] == 'searchResEntry' and testcase_id + 'to-be-deleted-1' in entry['dn']:
                    found = True
                    break
            self.assertTrue(found)

            # modify-delete an attribute and verify the sync
            # result = self.connection.modify(dn, {'businessCategory': (MODIFY_ADD, ['businessCategory-2-added', 'businessCategory-3-added'])})
            # if not self.connection.strategy.sync:
            #     _, result = self.connection.get_response(result)
            # else:
            #     result = self.connection.result
            # self.assertEqual(result['description'], 'success')
            result = self.connection.modify(dn, {'businessCategory': (MODIFY_DELETE, ['businessCategory-1-replaced'])})
            if not self.connection.strategy.sync:
                _, result = self.connection.get_response(result)
            else:
                result = self.connection.result
            self.assertEqual(result['description'], 'success')
            sleep(1)
            response = sync.loop()
            print('MOD-DEL ATTR', len(response), response[0]['attributes'])
            found = False
            for entry in response:
                if entry['type'] == 'searchResEntry' and testcase_id + 'to-be-deleted-1' in entry['dn']:
                    found = True
                    break
            self.assertTrue(found)

            # delete object and verify the sync
            self.connection.delete(dn)
            sleep(1)
            response = sync.loop()
            print('DEL OBJ', len(response), response[0]['attributes'])
            found = False
            for entry in response:
                if entry['type'] == 'searchResEntry' and testcase_id + 'to-be-deleted-1' in entry['dn']:
                    found = True
                    break

            self.assertTrue(found)

    def test_modify_password_as_administrator(self):
        if test_server_type == 'AD':
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'changed-password-1', attributes={'givenName': 'changed-password-1'}))
            dn = self.delete_at_teardown[-1][0]
            # test_connection = get_connection(bind=False, authentication=SIMPLE, simple_credentials=(dn, 'Rc1234abcd'))
            # test_connection.bind()
            # self.assertTrue(test_connection.bound)
            # connected_user = test_connection.extend.standard.who_am_i()
            # test_connection.unbind()
            # self.assertTrue('changed-password-1' in connected_user)

            new_password = 'Rc5678efgh'
            result = self.connection.extend.microsoft.modify_password(dn, new_password)
            self.assertEqual(result, True)
            # creates a second connection and tries to bind with the new password
            test_connection = get_connection(bind=False, authentication=SIMPLE, simple_credentials=(dn, new_password))
            test_connection.bind()
            connected_user = test_connection.extend.standard.who_am_i()
            test_connection.unbind()

            self.assertTrue('changed-password-1' in connected_user)

    def test_modify_password_as_normal_user(self):
        if test_server_type == 'AD':
            old_password = 'Ab1234cdef'
            new_password = 'Gh5678ijkl'
            self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'changed-password-2', password=old_password, attributes={'givenName': 'changed-password-2'}))
            dn = self.delete_at_teardown[-1][0]
            # creates a second connection and tries to bind with the new password
            test_connection = get_connection(bind=False, authentication=SIMPLE, simple_credentials=(dn, old_password))
            test_connection.bind()
            self.assertTrue(test_connection.bound)
            connected_user = test_connection.extend.standard.who_am_i()
            test_connection.unbind()
            self.assertTrue('changed-password-2' in connected_user)

            # changee the password
            result = self.connection.extend.microsoft.modify_password(dn, new_password, old_password)
            self.assertEqual(result, True)

            # tries to bind with the new password
            test_connection.password =  new_password
            test_connection.bind()
            connected_user = test_connection.extend.standard.who_am_i()
            test_connection.unbind()

            self.assertTrue('changed-password-2' in connected_user)
