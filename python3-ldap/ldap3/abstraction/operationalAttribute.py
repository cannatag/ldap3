"""
Created on 2014.02.09

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

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
from os import linesep

from .attribute import Attribute


class OperationalAttribute(Attribute):
    """
    Operational attribute/values object, it includes the search result of an operational attribute in an entry
    Attribute object is read only
    'values' contains the processed attribute values
    'rawValues' contains the unprocessed attribute values
    It doesn't have any AttrDef
    """

    def __init__(self, key, entry):
        self.__dict__['key'] = key
        self.__dict__['values'] = []
        self.__dict__['rawValues'] = []
        self.__dict__['entry'] = entry

    def __repr__(self):
        if len(self.values) == 1:
            r = self.key + ' [OPERATIONAL]: ' + str(self.values[0])
        elif len(self.values) > 1:
            r = self.key + ' [OPERATIONAL]: ' + str(self.values[0])
            filler = ' ' * (len(self.key) + 6)
            for value in sorted(self.values[1:]):
                r += linesep + filler + str(value)
        else:
            r = ''

        return r
