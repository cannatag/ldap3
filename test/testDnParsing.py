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
