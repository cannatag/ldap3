"""
Created on 2014.02.02

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

from . import AttrDef
from ldap3 import LDAPException


class ObjectDef(object):
    """
    AttrDefs are stored in a dictionary, the key is the friendly name defined in attrDef
    AttrDefs can be added and removedusing the += ad -= operators
    ObjectDef can be accessed either as a sequence and a dictionary. Wnen accessed the whole AttrDef instance is returned

    """

    def __init__(self, object_class=None):
        self.__dict__['object_class'] = object_class
        self.__dict__['_attributes'] = dict()

    def __repr__(self):
        r = 'object_class: ' + str(self.object_class) if self.object_class else ''
        for attr in self._attributes:
            r += linesep + '    ' + self._attributes[attr].__repr__() + ', '

        return r[:-2] if r[-2] == ',' else r

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, item):
        item = ''.join(item.split()).lower()
        for attr in self._attributes:
            if item == attr.lower():
                break
        else:
            raise LDAPException('key not present')

        return self._attributes[attr]

    def __setattr__(self, key, value):
        raise LDAPException('object is read only')

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        if isinstance(other, AttrDef):
            self.remove(other.key)
        elif isinstance(other, str):
            self.remove(other)

        return self

    def __iter__(self):
        for attribute in self._attributes:
            yield self._attributes[attribute]

    def __len__(self):
        return len(self._attributes)

    def __contains__(self, item):
        try:
            self.__getitem__(item)
        except:
            return False

        return True
    def add(self, definition=None):
        if isinstance(definition, str):
            element = AttrDef(definition)
            self.add(element)
        elif isinstance(definition, AttrDef):
            key = definition.key
            for attr in self._attributes:
                if key.lower() == attr.lower():
                    raise LDAPException('attribute already present')
            self._attributes[key] = definition
            self.__dict__[key] = definition
        elif isinstance(definition, list):
            for element in definition:
                self.add(element)
        else:
            raise LDAPException('unable to add element to object definition')

    def remove(self, item):
        key = None
        if isinstance(item, str):
            key = ''.join(item.split()).lower()
        elif isinstance(item, AttrDef):
            key = item.key

        if key:
            for attr in self._attributes:
                if item == attr.lower():
                    del self._attributes[attr]
                    break
            else:
                raise LDAPException('key not present')
        else:
            raise LDAPException('key must be str or AttrDef')

    def clear(self):
        self.__dict__['object_class'] = None
        self.__dict__['_attributes'] = dict()
