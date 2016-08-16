"""
"""

# Created on 2016.08.09
#
# Author: Giovanni Cannata
#
# Copyright 2016 Giovanni Cannata
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

from ldap3.abstract import ObjectDef, AttrDef, Reader, Writer
from test import test_base, get_connection, drop_connection, random_id, add_user
from ldap3 import ALL, MODIFY_REPLACE

testcase_id = random_id()


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(get_info=ALL, check_names=True)
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_create_objectdef_from_schema(self):
        o = ObjectDef(['inetorgPerson', 'person'], self.connection)
        self.assertEqual(o.cn.name, 'cn')

    def test_search_object(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abstract-1'))
        o = ObjectDef(['inetorgPerson', 'person'], self.connection)
        r = Reader(self.connection, o, '(cn=' + testcase_id + 'abstract-1)', test_base)
        r.search()
        self.assertEqual(len(r), 1)
        self.assertEqual(r.entries[0].cn, testcase_id + 'abstract-1')

    def test_set_single_value(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abstract-2'))
        o = ObjectDef(['inetorgPerson', 'person'], self.connection)
        r = Writer(self.connection, o, '(cn=' + testcase_id + 'abstract-2)', test_base)
        r.search()
        self.assertEqual(len(r.entries), 1)
        e = r.entries[0]
        e.uid = ['abstract-2-uid']
        self.assertEqual(e.uid.changes, [(MODIFY_REPLACE, ['abstract-2-uid'])])
        e.entry_commit()
        self.assertEqual(e.uid, 'abstract-2-uid')

    def test_set_multi_value(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abstract-3'))
        o = ObjectDef(['inetorgPerson', 'person'], self.connection)
        r = Writer(self.connection, o, '(cn=' + testcase_id + 'abstract-3)', test_base)
        r.search()
        self.assertEqual(len(r.entries), 1)
        e = r.entries[0]
        e.uid = ['abstract-3a-uid', 'abstract-3b-uid']
        self.assertEqual(e.uid.changes, [(MODIFY_REPLACE, ['abstract-3a-uid', 'abstract-3b-uid'])])
        e.entry_commit()
        self.assertEqual(e.uid, ['abstract-3a-uid', 'abstract-3b-uid'])
