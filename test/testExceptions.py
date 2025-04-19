"""
"""

# Created on 2014.05.10
#
# Author: Giovanni Cannata
#
# Copyright 2014 - 2025 Giovanni Cannata
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

from ldap3.core.exceptions import LDAPException, LDAPOperationsErrorResult, LDAPOperationResult


class Test(unittest.TestCase):
    def test_main_class_exception(self):
        e = LDAPException()
        self.assertTrue(isinstance(e, LDAPException))

    def test_subclassing_exception(self):
        e = LDAPOperationResult(1)
        self.assertTrue(isinstance(e, LDAPOperationsErrorResult))
