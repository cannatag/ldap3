"""
"""

# Created on 2013.06.06
#
# Author: Giovanni Cannata
#
# Copyright 2013, 2014, 2015, 2016 Giovanni Cannata
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

from ldap3 import MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE
from test.config import random_id, get_connection, add_user, \
    drop_connection

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()
        self.delete_at_teardown = []
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'modify-1', attributes={'givenName': 'givenname-1'}))

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_modify_replace(self):
        result = self.connection.modify(self.delete_at_teardown[0][0], {'givenName': (MODIFY_REPLACE, ['givenname-1-replaced']), 'sn': (MODIFY_REPLACE, ['sn-replaced'])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_modify_replace_with_get_request(self):
        result = self.connection.modify(self.delete_at_teardown[0][0], {'givenName': (MODIFY_REPLACE, ['givenname-1-replaced']), 'sn': (MODIFY_REPLACE, ['sn-replaced'])})
        if not self.connection.strategy.sync:
            _, result, request = self.connection.get_response(result, get_request=True)
            self.assertEqual(request['type'], 'modifyRequest')
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_modify_add(self):
        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': (MODIFY_ADD, ['businessCategory-2-added'])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_modify_delete_attribute_value(self):
        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': (MODIFY_ADD, ['businessCategory-3-added', 'businessCategory-4-added'])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': (MODIFY_DELETE, ['businessCategory-3-added'])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_modify_delete_attribute(self):
        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': (MODIFY_ADD, ['businessCategory-5-added', 'businessCategory-6-added'])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': (MODIFY_DELETE, [])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

    def test_delete_add_same_attribute(self):
        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': (MODIFY_ADD, ['businessCategory-7-added', 'businessCategory-8-added', 'businessCategory-9-added'])})
        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')

        result = self.connection.modify(self.delete_at_teardown[0][0], {'businessCategory': [(MODIFY_DELETE, ['businessCategory-8-added']), (MODIFY_ADD, ['business-Category-10-added'])]})

        if not self.connection.strategy.sync:
            _, result = self.connection.get_response(result)
        else:
            result = self.connection.result
        self.assertEqual(result['description'], 'success')
