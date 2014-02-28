"""
Created on 2014.01.12

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""

import unittest
from ldap3.abstraction import ObjectDef, AttrDef
from ldap3.abstraction import Reader
from ldap3.abstraction.reader import _createQueryDict


class Test(unittest.TestCase):
    def testCreateQueryDict(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        queryText = 'Common Name:=|john;Bob, Surname:=smith'
        # r = Reader(None, o, queryText, base='o=test')

        queryDict = _createQueryDict(queryText)

        self.assertDictEqual({'Common Name': '=|john;Bob', 'Surname': '=smith'}, queryDict)

    def testValidateQueryFilter(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        queryText = '|Common Name:=john;=Bob, Surname:=smith'
        r = Reader(None, o, queryText, base = 'o=test')

        r._validateQuery()

        self.assertEqual('Surname: =smith, |CommonName: =Bob;=john', r.validatedQuery)

    def testCreateQueryFilter(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        queryText = '|Common Name:=john;Bob, Surname:=smith'
        r = Reader(None, o, queryText, base = 'o=test')

        r._createQueryFilter()

        self.assertEqual('(&(sn=smith)(|(cn=Bob)(cn=john)))', r.queryFilter)

    def testCreateQueryFilterSingleAttributeSingleValue(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')

        queryText = 'Common Name:John'
        r = Reader(None, o, queryText, base = 'o=test')

        r._createQueryFilter()

        self.assertEqual('(cn=John)', r.queryFilter)

    def testCreateQueryFilterSingleAttributeMultipleValue(self):
        o = ObjectDef()
        o += AttrDef('cn', 'Common Name')

        queryText = '|Common Name:=john;=Bob'
        r = Reader(None, o, queryText, base='o=test')

        r._createQueryFilter()

        self.assertEqual('(|(cn=Bob)(cn=john))', r.queryFilter)

    def testCreateQueryFilterWithObjectClass(self):
        o = ObjectDef('inetOrgPerson')
        o += AttrDef('cn', 'Common Name')
        o += AttrDef('sn', 'Surname')
        o += AttrDef('givenName', 'Given Name')

        queryText = '|Common Name:=john;=Bob, Surname:=smith'
        r = Reader(None, o, queryText, base='o=test')

        r._createQueryFilter()

        self.assertEqual('(&(objectClass=inetOrgPerson)(sn=smith)(|(cn=Bob)(cn=john)))', r.queryFilter)
