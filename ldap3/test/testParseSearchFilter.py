# Created on 2013.06.04
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

from ldap3.operation.search import parse_filter, MATCH_EQUAL, MATCH_EXTENSIBLE


class Test(unittest.TestCase):
    def test_parse_search_filter_equality(self):
        f = parse_filter('(cn=admin)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EQUAL)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], b'admin')

    def test_parse_search_filter_extensible_syntax_1(self):
        f = parse_filter('(cn:caseExactMatch:=Fred Flintstone)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], b'Fred Flintstone')
        self.assertEqual(f.elements[0].assertion['matchingRule'], 'caseExactMatch')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], None)

    def test_parse_search_filter_extensible_syntax_2(self):
        f = parse_filter('(cn:=Betty Rubble)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], b'Betty Rubble')
        self.assertEqual(f.elements[0].assertion['matchingRule'], None)
        self.assertEqual(f.elements[0].assertion['dnAttributes'], None)

    def test_parse_search_filter_extensible_syntax_3(self):
        f = parse_filter('(sn:dn:2.4.6.8.10:=Barney Rubble)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'sn')
        self.assertEqual(f.elements[0].assertion['value'], b'Barney Rubble')
        self.assertEqual(f.elements[0].assertion['matchingRule'], '2.4.6.8.10')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], True)

    def test_parse_search_filter_extensible_syntax_4(self):
        f = parse_filter('(o:dn:=Ace Industry)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], 'o')
        self.assertEqual(f.elements[0].assertion['value'], b'Ace Industry')
        self.assertEqual(f.elements[0].assertion['matchingRule'], None)
        self.assertEqual(f.elements[0].assertion['dnAttributes'], True)

    def test_parse_search_filter_extensible_syntax_5(self):
        f = parse_filter('(:1.2.3:=Wilma Flintstone)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], None)
        self.assertEqual(f.elements[0].assertion['value'], b'Wilma Flintstone')
        self.assertEqual(f.elements[0].assertion['matchingRule'], '1.2.3')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], None)

    def test_parse_search_filter_extensible_syntax_6(self):
        f = parse_filter('(:DN:2.4.6.8.10:=Dino)', None)
        self.assertEqual(f.elements[0].tag, MATCH_EXTENSIBLE)
        self.assertEqual(f.elements[0].assertion['attr'], None)
        self.assertEqual(f.elements[0].assertion['value'], b'Dino')
        self.assertEqual(f.elements[0].assertion['matchingRule'], '2.4.6.8.''10')
        self.assertEqual(f.elements[0].assertion['dnAttributes'], True)


    # def test_parse_search_filter_bytes(self):
    #     bytes_filter = b'(cn=' + bytes([201,202,203,204,205]) + b')'
    #     f = parse_filter_bytes(bytes_filter)
