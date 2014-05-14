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

from ..core.exceptions import LDAPKeyError, LDAPAttributeError, LDAPEntryError


class Entry(object):
    """

    The Entry object contains a single entry from the result of an LDAP
    search.  Attributes can be accessed either by sequence, by assignment
    or as dictonary keys. Keys are not case sensitive.

    - The DN is retrieved by get_entry_dn()
    - The Reader reference is in get_entry_reader()
    - Raw attributes values are retrieved by the get_raw_attributes() and
      get_raw_attribute() methods

    The Entry object is read only
    """

    def __init__(self, dn, reader):
        self.__dict__['_attributes'] = dict()
        self.__dict__['_dn'] = dn
        self.__dict__['_raw_attributes'] = None
        self.__dict__['_reader'] = reader

    def __repr__(self):
        if self._dn:
            r = 'DN: ' + str(self._dn) + linesep
            if self._attributes:
                for attr in sorted(self._attributes):
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
                raise LDAPKeyError('key not found')
            return self._attributes[attr]

        raise LDAPKeyError('key must be a string')

    def __setattr__(self, item, value):
        if item in self._attributes:
            raise LDAPAttributeError('attribute is read only')
        else:
            raise LDAPEntryError('entry is read only')

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __eq__(self, other):
        if isinstance(other, Entry):
            return self._dn == other.get_entry_dn()

        return False

    def __lt__(self, other):
        if isinstance(other, Entry):
            return self._dn <= other.get_entry_dn()

        return False

    def get_entry_dn(self):
        return self._dn

    def get_entry_reader(self):
        return self._reader

    def get_raw_attributes(self):
        return self._raw_attributes

    def get_raw_attribute(self, name):
        return self._raw_attributes[name] if name in self._raw_attributes else None

    def refresh(self):
        temp_entry = self.get_entry_reader().search_object(self.get_entry_dn())
        self.__dict__['_attributes'] = temp_entry._attributes
        self.__dict__['_raw_attributes'] = temp_entry._raw_attributes
        del temp_entry
        return self
