"""
Created on 2013.06.04

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

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
from ldap3.operation.search import parseFilter, MATCH_EQUAL


class Test(unittest.TestCase):

    def testParseSearchFilter1(self):
        f = parseFilter('(cn=admin)')
        self.assertEqual(f.elements[0].tag, MATCH_EQUAL)
        self.assertEqual(f.elements[0].assertion['attr'], 'cn')
        self.assertEqual(f.elements[0].assertion['value'], 'admin')
