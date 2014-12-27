# Created on 2013.12.13
#
# @author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of pureLDAP.
#
# pureLDAP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pureLDAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pureLDAP in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import unittest

from ldap3 import Connection, STRATEGY_LDIF_PRODUCER, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
from test import test_base, dn_for_test, test_name_attr, test_moved


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = Connection(server=None, client_strategy=STRATEGY_LDIF_PRODUCER)
        self.connection.open()

    def tearDown(self):
        self.connection.unbind()
        self.assertFalse(self.connection.bound)

    def test_add_request_to_ldif(self):
        controls = list()
        controls.append(('2.16.840.1.113719.1.27.103.7', True, 'givenName'))
        controls.append(('2.16.840.1.113719.1.27.103.7', False, 'sn'))
        if str != bytes:  # python3
            controls.append(('2.16.840.1.113719.1.27.103.7', False, bytearray('\u00e0\u00e0', encoding='UTF-8')))
        else:
            controls.append(('2.16.840.1.113719.1.27.103.7', False, bytearray(unicode('\xe0\xe0', encoding='latin1'), encoding='UTF-8')))  # for python2 compatability
        controls.append(('2.16.840.1.113719.1.27.103.7', False, 'trailingspace '))
        self.connection.add(dn_for_test(test_base, 'test-add-operation'), 'iNetOrgPerson', {'objectClass': 'iNetOrgPerson', 'sn': 'test-add', test_name_attr: 'test-add-operation'}, controls=controls)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-add-operation,o=test' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 true: givenName' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 false: sn' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 false:: w6DDoA==' in response)
        self.assertTrue('control: 2.16.840.1.113719.1.27.103.7 false:: dHJhaWxpbmdzcGFjZSA=' in response)
        self.assertTrue('changetype: add' in response)
        self.assertTrue('objectClass: iNetOrgPerson' in response)
        self.assertTrue('sn: test-add' in response)
        self.assertTrue('cn: test-add-operation' in response)

    def test_delete_request_to_ldif(self):
        self.connection.strategy.order = dict(delRequest=['dn:', 'changetype', 'vers'])
        self.connection.delete(dn_for_test(test_base, 'test-del-operation'))
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-del-operation,o=test' in response)
        self.assertTrue('changetype: delete' in response)

    def test_modify_dn_request_to_ldif(self):
        result = self.connection.modify_dn(dn_for_test(test_base, 'test-modify-dn-operation'), test_name_attr + '=test-modified-dn-operation')
        if isinstance(result, int):
            self.connection.get_response(result)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-modify-dn-operation,o=test' in response)
        self.assertTrue('changetype: moddn' in response)
        self.assertTrue('newrdn: cn=test-modified-dn-operation' in response)
        self.assertTrue('deleteoldrdn: 1' in response)

    def test_move_dn_request_to_ldif(self):
        result = self.connection.modify_dn(dn_for_test(test_base, 'test-move-dn-operation'), test_name_attr + '=test-move-dn-operation', delete_old_dn=False, new_superior=test_moved)
        if isinstance(result, int):
            self.connection.get_response(result)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-move-dn-operation,o=test' in response)
        self.assertTrue('changetype: modrdn' in response)
        self.assertTrue('newrdn: cn=test-move-dn-operation' in response)
        self.assertTrue('deleteoldrdn: 0' in response)
        self.assertTrue('newsuperior: ou=moved,o=test' in response)

    def test_modify_add_to_ldif(self):
        result = self.connection.modify(dn_for_test(test_base, 'test-add-for-modify'), {'givenName': (MODIFY_ADD, ['test-modified-added'])})
        if isinstance(result, int):
            self.connection.get_response(result)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-add-for-modify,o=test' in response)
        self.assertTrue('changetype: modify' in response)
        self.assertTrue('add: givenName' in response)
        self.assertTrue('givenName: test-modified-added' in response)
        self.assertEqual('-', response[-1])

    def test_modify_replace_to_ldif(self):
        result = self.connection.modify(dn_for_test(test_base, 'test-add-for-modify'), {'givenName': (MODIFY_REPLACE, ['test-modified-replace'])})
        if isinstance(result, int):
            self.connection.get_response(result)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-add-for-modify,o=test' in response)
        self.assertTrue('changetype: modify' in response)
        self.assertTrue('replace: givenName' in response)
        self.assertTrue('givenName: test-modified-replace' in response)
        self.assertEqual('-', response[-1])

    def test_modify_delete_to_ldif(self):
        result = self.connection.modify(dn_for_test(test_base, 'test-add-for-modify'), {'givenName': (MODIFY_DELETE, ['test-modified-added2'])})
        if isinstance(result, int):
            self.connection.get_response(result)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=test-add-for-modify,o=test' in response)
        self.assertTrue('changetype: modify' in response)
        self.assertTrue('delete: givenName' in response)
        self.assertTrue('givenName: test-modified-added2' in response)
        self.assertEqual('-', response[-1])

    def test_multiple_modify_to_ldif(self):
        # from rfc 2849 example
        result = self.connection.modify('cn=Paula Jensen, ou=Product Development, dc=airius, dc=com',
                                        {'postaladdress': (MODIFY_ADD, ['123 Anystreet $ Sunnyvale, CA $ 94086']), 'description': (MODIFY_DELETE, []), 'telephonenumber': (MODIFY_REPLACE, ['+1 408 555 1234', '+1 408 555 5678']),
                                         'facsimiletelephonenumber': (MODIFY_DELETE, ['+1 408 555 9876'])})
        if isinstance(result, int):
            self.connection.get_response(result)
        response = self.connection.response
        self.assertTrue('version: 1' in response)
        self.assertTrue('dn: cn=Paula Jensen, ou=Product Development, dc=airius, dc=com' in response)
        self.assertTrue('changetype: modify' in response)
        self.assertTrue('delete: facsimiletelephonenumber' in response)
        self.assertTrue('facsimiletelephonenumber: +1 408 555 9876' in response)
        self.assertTrue('replace: telephonenumber' in response)
        self.assertTrue('telephonenumber: +1 408 555 1234' in response)
        self.assertTrue('telephonenumber: +1 408 555 5678' in response)
        self.assertTrue('add: postaladdress' in response)
        self.assertTrue('postaladdress: 123 Anystreet $ Sunnyvale, CA $ 94086' in response)
        self.assertTrue('delete: description' in response)
        self.assertEqual('-', response[-1])
