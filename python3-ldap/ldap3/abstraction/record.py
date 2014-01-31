"""
Created on 2014.01.06

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


class Record(object):

    def __init__(self, dn):
        self.__dict__['_attributes'] = dict()
        self._dn = dn
        self._rawAttributes = None

    def __repr__(self):
        if self._dn:
            r = 'DN: ' + str(self._dn) + linesep
            if self._attributes:
                for attr in self._attributes:
                    r += ' ' * 4 + repr(self._attributes[attr]) + linesep

            return r
        else:
            return object.__repr__(self)

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        for attribute in self._attributes:
            yield self._attributes[attribute]
        raise StopIteration

    def __getitem__(self, item):
        return self._attributes[item]

    def entryDN(self):
        return self._dn

    def __setattr__(self, key, value):
        if key in self._attributes:
            raise Exception('Attribute is readonly')
        else:
            object.__setattr__(self, key, value)
