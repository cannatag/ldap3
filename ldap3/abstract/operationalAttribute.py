"""
"""

# Created on 2014.02.09
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016 Giovanni Cannata
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

from os import linesep

from .attribute import Attribute
from ..utils.repr import to_stdout_encoding


# noinspection PyUnresolvedReferences,PyMissingConstructor
class OperationalAttribute(Attribute):
    """Operational attribute/values object. Include the search result of an
    operational attribute in an entry

    OperationalAttribute object is read only

    - values: contains the processed attribute values
    - raw_values: contains the unprocessed attribute values

    It doesn't have any AttrDef

    """
    def __init__(self, key, entry):
        self.key = key
        self.entry = entry
        self.values = []
        self.raw_values = []

    def __repr__(self):
        if len(self.values) == 1:
            r = self.key + ' [OPERATIONAL]: ' + to_stdout_encoding(self.values[0])
        elif len(self.values) > 1:
            r = self.key + ' [OPERATIONAL]: ' + to_stdout_encoding(self.values[0])
            filler = ' ' * (len(self.key) + 6)
            for value in sorted(self.values[1:]):
                r += linesep + filler + to_stdout_encoding(value)
        else:
            r = ''

        return r
