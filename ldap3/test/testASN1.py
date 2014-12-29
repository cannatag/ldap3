# Created on 2013.05.15
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

from ldap3.protocol.rfc4511 import rangeInt0ToMaxConstraint


class Test(unittest.TestCase):
    def test_constraint_max_int(self):
        msg = None
        try:
            rangeInt0ToMaxConstraint(-1)
        except Exception as e:
            msg = e.args[0]
        self.assertEqual('ValueRangeConstraint(0, Integer(2147483647)) failed at: "-1"', msg)
