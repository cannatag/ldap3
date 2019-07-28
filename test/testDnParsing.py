"""
"""

# Created on 2014.09.15
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2018 Giovanni Cannata
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

from ldap3.utils.dn import parse_dn as p


class Test(unittest.TestCase):
    def test_parse_dn_single(self):
        parsed = p('cn=admin')
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0], ('cn', 'admin', ''))

    def test_parse_dn_single_multi_rdn(self):
        parsed = p('cn=admin+email=admin@site.com')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], ('cn', 'admin', '+'))
        self.assertEqual(parsed[1], ('email', 'admin@site.com', ''))

    def test_parse_dn_escaped_single_multi_rdn(self):
        parsed = p('cn=\\\\\\+admin+email=admin@site.com')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], ('cn', '\\\\\\+admin', '+'))
        self.assertEqual(parsed[1], ('email', 'admin@site.com', ''))

    def test_parse_dn_double(self):
        parsed = p('cn=user1,o=users')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], ('cn', 'user1', ','))
        self.assertEqual(parsed[1], ('o', 'users', ''))

    def test_parse_dn_multi(self):
        parsed = p('cn=user1,ou=users,dc=branch,dc=company,c=IT')
        self.assertEqual(len(parsed), 5)
        self.assertEqual(parsed[0], ('cn', 'user1', ','))
        self.assertEqual(parsed[1], ('ou', 'users', ','))
        self.assertEqual(parsed[2], ('dc', 'branch', ','))
        self.assertEqual(parsed[3], ('dc', 'company', ','))
        self.assertEqual(parsed[4], ('c', 'IT', ''))

    def test_parse_dn_multi_type(self):
        parsed = p('cn=user1+sn=surname1,o=users')
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], ('cn', 'user1', '+'))
        self.assertEqual(parsed[1], ('sn', 'surname1', ','))
        self.assertEqual(parsed[2], ('o', 'users', ''))

    def test_parse_dn_escaped_single(self):
        parsed = p('cn=admi\\,n')
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0], ('cn', 'admi\\,n', ''))

    def test_parse_dn_escaped_double(self):
        parsed = p('cn=us\\=er1,o=us\\,ers')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], ('cn', 'us\\=er1', ','))
        self.assertEqual(parsed[1], ('o', 'us\\,ers', ''))

    def test_parse_dn_escaped_double_1(self):
        parsed = p('cn=\\\\,o=\\\\')
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], ('cn', '\\\\', ','))
        self.assertEqual(parsed[1], ('o', '\\\\', ''))

    def test_parse_dn_escaped_multi(self):
        parsed = p('cn=us\\,er1,ou=us\\08ers,dc=br\\,anch,dc=company,c=IT')
        self.assertEqual(len(parsed), 5)
        self.assertEqual(parsed[0], ('cn', 'us\\,er1', ','))
        self.assertEqual(parsed[1], ('ou', 'us\\08ers', ','))
        self.assertEqual(parsed[2], ('dc', 'br\\,anch', ','))
        self.assertEqual(parsed[3], ('dc', 'company', ','))
        self.assertEqual(parsed[4], ('c', 'IT', ''))

    def test_parse_dn_escaped_multi_type(self):
        parsed = p('cn=us\\+er1+sn=su\\,rname1,o=users')
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], ('cn', 'us\\+er1', '+'))
        self.assertEqual(parsed[1], ('sn', 'su\\,rname1', ','))
        self.assertEqual(parsed[2], ('o', 'users', ''))

    def test_parse_dn_unescaped_single(self):
        parsed = p('cn=admi,n', escape=True)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0], ('cn', 'admi\\,n', ''))

    def test_parse_dn_unescaped_double(self):
        parsed = p('cn=us=er1,o=us,ers', escape=True)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0], ('cn', 'us\\=er1', ','))
        self.assertEqual(parsed[1], ('o', 'us\\,ers', ''))

    def test_parse_dn_unescaped_multi(self):
        parsed = p('cn=us,er1,ou=use<rs,dc=br+anch,dc=company,c=IT', escape=True)
        self.assertEqual(len(parsed), 5)
        self.assertEqual(parsed[0], ('cn', 'us\\,er1', ','))
        self.assertEqual(parsed[1], ('ou', 'use\\<rs', ','))
        self.assertEqual(parsed[2], ('dc', 'br\\+anch', ','))
        self.assertEqual(parsed[3], ('dc', 'company', ','))
        self.assertEqual(parsed[4], ('c', 'IT', ''))

    def test_parse_dn_unescaped_multi_type(self):
        parsed = p('cn=us+er1+sn=su,rname1,o=users', escape=True)
        self.assertEqual(len(parsed), 3)
        self.assertEqual(parsed[0], ('cn', 'us\\+er1', '+'))
        self.assertEqual(parsed[1], ('sn', 'su\\,rname1', ','))
        self.assertEqual(parsed[2], ('o', 'users', ''))

    def pair_generator(self):
        # escaped = DQUOTE / PLUS / COMMA / SEMI / LANGLE / RANGLE
        escaped = ['"', '+', ',', ';', '<', '>']
        # special = escaped / SPACE / SHARP / EQUALS
        special = escaped + [' ', '#', '=']
        ESC = ['\\']
        # hexpair = HEX HEX
        hexpairs = ['00', '99', 'aa', 'AA', 'ff', 'FF', 'aF', 'Af']
        # pair = ESC ( ESC / special / hexpair )
        pair = self.combine_strings(ESC, ESC + special + hexpairs)
        return pair

    def test_parse_dn_pair(self):
        for onepair in self.pair_generator():
            for attributeValue, mode in [
                (onepair, "alone"),
                ("a" + onepair + "b", "between"),
                ("a" + onepair, "after"),
                (onepair + "b", "before")
            ]:
                for separator in [None, '+', ',']:

                    if not separator:
                        dn = r'cn={0}'.format(attributeValue)
                        expected = [('cn', attributeValue, '')]
                    else:
                        dn = r'cn={0}{1}ou={0}'.format(attributeValue, separator)
                        expected = [('cn', attributeValue, separator), ('ou', attributeValue, '')]

                    with self.subTest(pair=onepair, separator=separator, mode=mode, input=dn):
                        self._test_parse_dn(
                            dn,
                            expected
                        )

    def combine_strings(self, *args):
        if len(args) == 0: raise Exception("Invalid parameter")
        if len(args) == 1:
            for variant in args[0]:
                yield variant
        else:
            for head in args[0]:
                for tail in self.combine_strings(*args[1:]):
                    variant = head + tail
                    yield variant

    def test_combine_strings(self):
        variants = set(self.combine_strings(['a', 'b'], ['x', 'y']))
        self.assertEqual(variants, {'ax', 'ay', 'bx', 'by'})

    def test_combine_strings_empty1(self):
        variants = set(self.combine_strings([], ['x', 'y']))
        self.assertEqual(len(variants), 0)

    def test_combine_strings_empty2(self):
        variants = set(self.combine_strings(['a', 'b'], []))
        self.assertEqual(len(variants), 0)

    def _test_parse_dn(self, input, expected):
        parsed = p(input, escape=False)
        self.assertEqual(parsed, expected)

    def test_unit_test_deep_equality(self):
        self.assertEqual([], [])
        self.assertNotEqual([], [()])
        self.assertEqual([()], [()])
        self.assertNotEqual([()], [(), ()])
        self.assertNotEqual([()], [('b')])
        self.assertEqual([('a')], [('a')])
        self.assertNotEqual([('a')], [('b')])
        self.assertEqual([('a', 'b', 'x'), ('a', 'b', 'x')], [('a', 'b', 'x'), ('a', 'b', 'x')])
        self.assertNotEqual([('a', 'b', 'x'), ('a', 'b', 'x')], [('a', 'b', 'x'), ('a', 'b', 'y')])
        self.assertNotEqual([('1')], [(1)])
