"""
"""

# Created on 2014.01.12
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016 Giovanni Cannata
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
from ldap3.abstract.cursor import _create_query_dict
from test.config import test_base, get_connection, drop_connection


class Test(unittest.TestCase):
    def setUp(self):
        self.connection = get_connection(check_names=True)

    def tearDown(self):
        drop_connection(self.connection)

    def test_create_query_dict(self):
        query_text = 'Common Name:=|john;Bob, Surname:=smith'
        query_dict = _create_query_dict(query_text)
        self.assertEqual(query_dict['Common Name'], '=|john;Bob')
        self.assertEqual(query_dict['Surname'], '=smith')
        self.assertEqual(len(query_dict), 2)

    def test_validate_query_filter(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        query_text = '|Common Name:=john;=Bob, Surname:=smith'
        r = Reader(self.connection, o, test_base, query_text)

        r._validate_query()

        self.assertEqual('Surname: =smith, |CommonName: =Bob;=john', r.validated_query)

    def test_create_query_filter(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        query_text = '|Common Name:=john;Bob, Surname:=smith'
        r = Reader(self.connection, o, test_base, query_text)

        r._create_query_filter()

        self.assertEqual('(&(sn=smith)(|(cn=Bob)(cn=john)))', r.query_filter)

    def test_create_query_filter_single_attribute_single_value(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')

        query_text = 'Common Name:John'
        r = Reader(self.connection, o, test_base, query_text)

        r._create_query_filter()

        self.assertEqual('(cn=John)', r.query_filter)

    def test_create_query_filter_single_attribute_multiple_value(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')

        query_text = '|Common Name:=john;=Bob'
        r = Reader(self.connection, o, test_base, query_text)

        r._create_query_filter()

        self.assertEqual('(|(cn=Bob)(cn=john))', r.query_filter)

    def test_create_query_filter_with_object_class(self):
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        query_text = '|Common Name:=john;=Bob, Surname:=smith'
        r = Reader(self.connection, o, test_base, query_text)

        r._create_query_filter()

        self.assertEqual('(&(objectClass=inetOrgPerson)(sn=smith)(|(cn=Bob)(cn=john)))', r.query_filter)
