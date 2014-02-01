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


class Entry(object):

    def __init__(self, dn, reader):
        self.__dict__['_attributes'] = dict()
        self.__dict__['_dn'] = dn
        self.__dict__['_rawAttributes'] = None
        self.__dict__['_reader'] = reader

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

    def __contains__(self, item):
        return True if self.__getitem__(item) else False

    def __getattr__(self, item):
        if isinstance(item, str):
            item = ''.join(item.split()).lower()
            for attr in self._attributes:
                if item == attr.lower():
                    break
            else:
                raise Exception('invalid key')

            if len(self._attributes[attr].values) == 1 and self._reader.noSingleValueList:
                return self._attributes[attr].values[0]

            return self._attributes[attr].values

        raise Exception('invalid key')

    def __getitem__(self, item):
        return self.__getattr__(item)

    @property
    def entryDN(self):
        return self._dn

    @property
    def entryReader(self):
        return self._reader

    def __setattr__(self, item, value):
        if item in self._attributes:
            raise Exception('Attribute is readonly')
        else:
            raise Exception('entry is read only')
