"""
Created on 2013.08.26

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
from unicodedata import lookup

from ldap3.protocol.sasl.sasl import validateSimplePassword


class Test(unittest.TestCase):
    def testValidSimpleAlphanumericPassword(self):
        password = 'abcdefg1234567890ABCDEFG'
        validated = validateSimplePassword(password)
        self.assertEqual(password, validated)

    def testValidSimpleAlphanumericPasswordWithASCIICharacters(self):
        password = 'abcdefg1234567890ABCDEFG!"$%&/()='
        validated = validateSimplePassword(password)
        self.assertEqual(password, validated)

    def testValidSimpleAlphanumericPasswordWithNonASCIICharacters(self):
        password = ''.join(['123', lookup('POUND SIGN'), 'abc'])
        validated = validateSimplePassword(password)
        self.assertEqual(password, validated)

    def testValidSimpleAlphanumericPasswordWithMappedToNothingCharacters(self):
        password = ''.join(['123', lookup('SOFT HYPHEN'), 'abc'])
        validated = validateSimplePassword(password)
        self.assertEqual('123abc', validated)

    def testValidSimpleAlphanumericPasswordWithMappedToSpace(self):
        password = ''.join(['123', lookup('FIGURE SPACE'), 'abc'])
        validated = validateSimplePassword(password)
        self.assertEqual('123 abc', validated)
