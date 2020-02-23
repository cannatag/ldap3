"""
"""
# Created on 2014.01.19
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2020 Giovanni Cannata
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

from ldap3 import ObjectDef, AttrDef, Reader
from test.config import test_base, add_user, add_group, get_connection, drop_connection, random_id, test_server_type, test_multivalued_attribute, test_singlevalued_attribute

testcase_id = ''


class Test(unittest.TestCase):
    def setUp(self):
        global testcase_id
        testcase_id = random_id()
        self.connection = get_connection()
        self.delete_at_teardown = []

    def tearDown(self):
        drop_connection(self.connection, self.delete_at_teardown)
        self.assertFalse(self.connection.bound)

    def test_search_filter_with_object_class(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-3'))
        self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'abs-grp', self.delete_at_teardown))
        reverse = lambda a, e: e[::-1]
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef(test_multivalued_attribute, 'Given Name', post_query=reverse)

        query_text = 'Common Name:=' + testcase_id + 'abs-*'
        r = Reader(self.connection, o, test_base, query_text)

        results = r.search()
        self.assertEqual(len(results), 3)

    def test_search_with_dereference(self):
        reverse = lambda a, e: e[::-1]

        def raise_parentheses_rank(_, l):
            up = {'(': '[', ')': ']', '[': '{', ']': '}', '{': '<', '}': '>'}
            r = []
            for e in l:
                s = ''
                for c in e:
                    s += up[c] if c in up else c
                r.append(s)

            return r

        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-4'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-5'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-6'))
        self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'abstract-group', self.delete_at_teardown))
        ou = ObjectDef('inetOrgPerson')
        ou += AttrDef('cn', 'Common Name', post_query=reverse)
        ou += AttrDef('sn', 'Surname')
        ou += AttrDef(test_multivalued_attribute, 'Given Name', post_query=raise_parentheses_rank)
        ou += AttrDef('ACL')
        qu = 'Common Name: ' + testcase_id + 'abs-*'
        ru = Reader(self.connection, ou, test_base, qu)
        lu = ru.search()
        self.assertEqual(len(lu), 3)

        og = ObjectDef('groupOfNames')
        og += AttrDef('member', dereference_dn=ou)
        og += 'cn'
        qg = 'cn := ' + testcase_id + 'abstract-group'
        rg = Reader(self.connection, og, test_base, qg)
        lg = rg.search()
        self.assertEqual(len(lg), 1)

        eg = lg[0]
        mg = eg.member
        self.assertEqual(len(mg), 3)
        ug = eg.member[0]
        self.assertTrue(str(ug.surname) in ['abs-4', 'abs-5', 'abs-6'])

    def test_search_with_pre_query(self):
        change = lambda attr, value: testcase_id + 'abs-*'

        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-7'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-8'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-9'))
        self.delete_at_teardown.append(add_group(self.connection, testcase_id, 'abstract-group', self.delete_at_teardown))

        ou = ObjectDef('inetOrgPerson')
        ou += AttrDef('cn', 'Common Name', pre_query=change)
        ou += AttrDef('sn', 'Surname')
        ou += AttrDef(test_multivalued_attribute, 'Given Name')
        ou += AttrDef('ACL')
        qu = 'Common Name := bug'
        ru = Reader(self.connection, ou, test_base, qu)
        lu = ru.search()
        self.assertEqual(len(lu), 3)

    def test_search_with_default(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-10'))

        ou = ObjectDef('inetOrgPerson')
        ou += AttrDef('cn', 'CommonName')
        ou += AttrDef('employeeType', key='Employee', default='not employed')
        qu = 'CommonName := ' + testcase_id + 'abs-10'
        ru = Reader(self.connection, ou, test_base, qu)
        lu = ru.search()
        self.assertEqual(str(lu[0].employee), 'not employed')

    def test_search_with_falsy_default(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-11'))

        ou = ObjectDef('inetOrgPerson')
        ou += AttrDef('cn', 'CommonName')
        ou += AttrDef('employeeType', key='Employee', default='')
        qu = 'CommonName := ' + testcase_id + 'abs-11'
        ru = Reader(self.connection, ou, test_base, qu)
        lu = ru.search()
        self.assertEqual(lu[0].employee.value, '')

    def test_search_with_None_default(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'abs-12'))

        ou = ObjectDef('inetOrgPerson')
        ou += AttrDef('cn', 'CommonName')
        ou += AttrDef('employeeType', key='Employee', default=None)
        qu = 'CommonName := ' + testcase_id + 'abs-12'
        ru = Reader(self.connection, ou, test_base, qu)
        lu = ru.search()
        self.assertEqual(lu[0].employee.value, None)

    def test_find_entry_with_text_index_match(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3'))
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef(test_multivalued_attribute, 'Given Name')

        query_text = 'Common Name:=' + testcase_id + 'mat-*'
        r = Reader(self.connection, o, test_base, query_text)

        results = r.search()
        self.assertEqual(len(results), 3)
        try:  # multiple matches
            e = r['match']
        except  KeyError:
            pass

        e = r['-2']  # exact match
        self.assertTrue('mat-2' in e.entry_dn)

        try:
            e = r['no-match']  # no match
        except KeyError:
            pass

    def test_match_dn_in_cursor(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3'))
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef(test_multivalued_attribute, 'Given Name')

        query_text = 'Common Name:=' + testcase_id + 'mat-*'
        r = Reader(self.connection, o, test_base, query_text)

        results = r.search()
        self.assertEqual(len(results), 3)

        e = r.match_dn('mat')  # multiple matches
        self.assertEqual(len(e), 3)
        e = r.match_dn('-2')  # single match
        self.assertEqual(len(e), 1)
        e = r.match_dn('no-match')  # no match
        self.assertEqual(len(e), 0)

    def test_match_in_single_attribute(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1', attributes={test_multivalued_attribute: ['givenname-1', 'givenname-1a']}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2', attributes={test_multivalued_attribute: ['givenname-2', 'givenname-2a']}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3', attributes={test_multivalued_attribute: ['givenname-3', 'givenname-3a']}))
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef(test_multivalued_attribute, 'Given Name')

        query_text = 'Common Name:=' + testcase_id + 'mat-*'
        r = Reader(self.connection, o, test_base, query_text)

        results = r.search()
        self.assertEqual(len(results), 3)

        e = r.match('Given Name', 'name')  # multiple matches
        self.assertEqual(len(e), 3)
        e = r.match('Given Name', '2a')  # single match
        self.assertEqual(len(e), 1)
        e = r.match('Given Name', 'no-match')  # no match
        self.assertEqual(len(e), 0)

    def test_match_in_multiple_attribute(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1', attributes={test_multivalued_attribute: ['givenname-1', 'givenname-1a'], 'street': '1a'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2', attributes={test_multivalued_attribute: ['givenname-2', 'givenname-2a'], 'street': '3a'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3', attributes={test_multivalued_attribute: ['givenname-3', 'givenname-3a'], 'street': '4a'}))
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef(test_multivalued_attribute, 'Given Name')
        o += AttrDef('street', 'Street')

        query_text = 'Common Name:=' + testcase_id + 'mat-*'
        r = Reader(self.connection, o, test_base, query_text)

        results = r.search()
        self.assertEqual(len(results), 3)

        e = r.match(['Given Name', 'Street'], '3a')  # multiple matches
        self.assertEqual(len(e), 2)
        e = r.match(['Given Name', 'street'], '1a')  # single match
        self.assertEqual(len(e), 1)
        e = r.match(['Given Name', 'street'], 'no-match')  # no match
        self.assertEqual(len(e), 0)

    def test_match_in_single_attribute_with_schema(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1', attributes={test_singlevalued_attribute: 'FALSE'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2', attributes={test_singlevalued_attribute: 'FALSE'}))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3', attributes={test_singlevalued_attribute: 'TRUE'}))
        r = Reader(self.connection, 'inetorgperson', test_base, 'cn:=' + testcase_id + 'mat-*')

        results = r.search()
        self.assertEqual(len(results), 3)

        e = r.match(test_singlevalued_attribute, 'FALSE')
        self.assertEqual(len(e), 2)
        e = r.match(test_singlevalued_attribute, 'fAlSe')
        self.assertEqual(len(e), 2)

    def test_paged_search_accumulator_with_schema(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-4'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-5'))
        r = Reader(self.connection, 'inetorgperson', test_base, 'cn:=' + testcase_id + 'mat-*')
        entries = r.search_paged(2, True, generator=False, attributes=['cn'])
        self.assertEqual(len(entries), 5)

    def test_paged_search_generator_with_schema(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-2'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-3'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-4'))
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-5'))
        r = Reader(self.connection, 'inetorgperson', test_base, 'cn:=' + testcase_id + 'mat-*')
        entries = r.search_paged(2, True, generator=True, attributes=['cn'])
        cont = 0
        for _ in entries:
            cont += 1
        self.assertEqual(cont, 5)

    def test_paged_search_accumulator_with_schema_single_entry(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        r = Reader(self.connection, 'inetorgperson', test_base, 'cn:=' + testcase_id + 'mat-*')
        entries = r.search_paged(2, True, generator=False, attributes=['cn'])
        self.assertEqual(len(entries), 1)

    def test_paged_search_generator_with_schema_single_entry(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        r = Reader(self.connection, 'inetorgperson', test_base, 'cn:=' + testcase_id + 'mat-*')
        entries = r.search_paged(2, True, generator=True, attributes=['cn'])
        cont = 0
        for _ in entries:
            cont += 1
        self.assertEqual(cont, 1)

    def test_paged_search_accumulator_with_schema_base_object(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        r = Reader(self.connection, 'inetorgperson', self.delete_at_teardown[0][0])
        entries = r.search_paged(2, True, generator=False, attributes=['cn'])
        self.assertEqual(len(entries), 1)

    def test_paged_search_generator_with_schema_base_object(self):
        self.delete_at_teardown.append(add_user(self.connection, testcase_id, 'mat-1'))
        r = Reader(self.connection, 'inetorgperson', self.delete_at_teardown[0][0])
        entries = r.search_paged(2, True, generator=True, attributes=['cn'])
        cont = 0
        for _ in entries:
            cont += 1
        self.assertEqual(cont, 1)
