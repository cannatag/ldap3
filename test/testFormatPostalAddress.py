# encoding: utf-8
"""
"""

# Created on 2022.02.20
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

from ldap3.protocol.formatters.formatters import format_postal


class Test(unittest.TestCase):
    def test_format_postal(self):
        # Trivial:
        self.assertEqual(format_postal(b'abc'), 'abc')

        # Escaped characters:
        self.assertEqual(format_postal(b'$'), '\n')
        self.assertEqual(format_postal(br'\24'), '$')
        self.assertEqual(format_postal(br'\5C'), '\\')
        self.assertEqual(format_postal(br'\5c'), '\\')

        # Examples from RFC 4517:
        self.assertEqual(
            format_postal(b'1234 Main St.$Anytown, CA 12345$USA'),
            '1234 Main St.\nAnytown, CA 12345\nUSA',
        )
        self.assertEqual(
            format_postal(br'\241,000,000 Sweepstakes$PO Box 1000000$Anytown, CA 12345$USA'),
            '$1,000,000 Sweepstakes\nPO Box 1000000\nAnytown, CA 12345\nUSA',
        )

        # UTF-8:
        self.assertEqual(
            format_postal(b'Z\xC3\xBCrich HB$Bahnhofplatz$8001 Z\xC3\xBCrich$Schweiz'),
            u'Zürich HB\nBahnhofplatz\n8001 Zürich\nSchweiz',
        )
