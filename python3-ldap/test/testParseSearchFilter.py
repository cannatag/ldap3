"""
+reated on 2013.06.04

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

This file is part of python3-ldap.

/ython3-ldap is free software: you can redistribute it and/or modify
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
from ldap3.operation.search import parseFilter, MATCH_EQUAL, MATCH_EXTENSIBLE


class Test(unittest.TestCase):
    def testParseSearchFilterEquality(self):
        f = parseFilter('(cn=admin)')
        self.assertEqual(f.elements[0].tag, MATCH_EQUAL)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], 'admin')

    def testParseSearchFilterExtensible1(self):
        f = parseFilter('(cn:caseExactMatch:=Fred Flintstone)')
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], 'Fred Flintstone')
        self.assertEqual(f.elements[0].assertion['matchingRule'], 'caseExactMatch')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], None)

    def testParseSearchFilterExtensible2(self):
        f = parseFilter('(cn:=Betty Rubble)')
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], 'Betty Rubble')
        self.assertEqual(f.elements[0].assertion['matchingRule'], None)
        self.assertEqual(f.elements[0].assertion['dnAttributes'], None)

    def testParseSearchFilterExtensible3(self):
        f = parseFilter('(sn:dn:2.4.6.8.10:=Barney Rubble)')
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'sn')
        self.assertEqual(f.elements[0].assertion['value'], 'Barney Rubble')
        self.assertEqual(f.elements[0].assertion['matchingRule'], '2.4.6.8.10')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], True)

    def testParseSearchFilterExtensible4(self):
        f = parseFilter('(o:dn:=Ace Industry)')
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'o')
        self.assertEqual(f.elements[0].assertion['value'], 'Ace Industry')
        self.assertEqual(f.elements[0].assertion['matchingRule'], None)
        self.assertEqual(f.elements[0].assertion['dnAttributes'], True)

    def testParseSearchFilterExtensible5(self):
        f = parseFilter('(:1.2.3:=Wilma Flintstone)')
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], None)
        self.assertEqual(f.elements[0].assertion['value'], 'Wilma Flintstone')
        self.assertEqual(f.elements[0].assertion['matchingRule'], '1.2.3')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], None)

    def testParseSearchFilterExtensible6(self):
        f = parseFilter('(:DN:2.4.6.8.10:=Dino)')
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], None)
        self.assertEqual(f.elements[0].assertion['value'], 'Dino')
        self.assertEqual(f.elements[0].assertion['matchingRule'], '2.4.6.8.''10')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], True)
