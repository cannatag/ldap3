# Created on 2014.01.12
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

from ldap3.abstract import ObjectDef, AttrDef, Reader
from ldap3.abstract.reader import _create_query_dict


class Test(unittest.TestCase):
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
        r = Reader(None, o, query_text, base='o=test')

        r._validate_query()

        self.assertEqual('Surname: =smith, |CommonName: =Bob;=john', r.validated_query)

    def test_create_query_filter(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        query_text = '|Common Name:=john;Bob, Surname:=smith'
        r = Reader(None, o, query_text, base='o=test')

        r._create_query_filter()

        self.assertEqual('(&(sn=smith)(|(cn=Bob)(cn=john)))', r.query_filter)

    def test_create_query_filter_single_attribute_single_value(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')

        query_text = 'Common Name:John'
        r = Reader(None, o, query_text, base='o=test')

        r._create_query_filter()

        self.assertEqual('(cn=John)', r.query_filter)

    def test_create_query_filter_single_attribute_multiple_value(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')

        query_text = '|Common Name:=john;=Bob'
        r = Reader(None, o, query_text, base='o=test')

        r._create_query_filter()

        self.assertEqual('(|(cn=Bob)(cn=john))', r.query_filter)

    def test_create_query_filter_with_object_class(self):
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        query_text = '|Common Name:=john;=Bob, Surname:=smith'
        r = Reader(None, o, query_text, base='o=test')

        r._create_query_filter()

        self.assertEqual('(&(objectClass=inetOrgPerson)(sn=smith)(|(cn=Bob)(cn=john)))', r.query_filter)
