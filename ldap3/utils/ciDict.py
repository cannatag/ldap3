"""
"""

# Created on 2014.08.23
#
# Author: Giovanni Cannata
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

import collections

from .. import SEQUENCE_TYPES


class CaseInsensitiveDict(collections.MutableMapping):
    if bytes == str:  # python2
        _case_insensitive_types = (str, unicode)
    else:  # python3
        _case_insensitive_types = (str,)

    def __init__(self, other=None, **kwargs):
        self._store = dict()
        if other or kwargs:
            if other is None:
                other = dict()
            self.update(other, **kwargs)

    def _getkey(self, key):
        if isinstance(key, CaseInsensitiveDict._case_insensitive_types):
            for stored_key in self._store:
                if isinstance(stored_key, CaseInsensitiveDict._case_insensitive_types):
                    if key.lower() == stored_key.lower():
                        key = stored_key
                        break
        return key

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except Exception:
            return False

    def __delitem__(self, key):
        del self._store[self._getkey(key)]

    def __setitem__(self, key, item):
        self._store[self._getkey(key)] = item

    def __getitem__(self, key):
        return self._store[self._getkey(key)]

    def __iter__(self):
        return self._store.__iter__()

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return repr(self._store)

    def __str__(self):
        return str(self._store)

    def keys(self):
        return self._store.keys()

    def values(self):
        return self._store.values()

    def __eq__(self, other):
        if not isinstance(other, (collections.Mapping, dict)):
            return NotImplemented

        if isinstance(other, CaseInsensitiveDict):
            if isinstance(self.items(), SEQUENCE_TYPES):  # python 2
                if len(self.items()) != len(other.items()):
                    return False
                else:
                    for key, value in self.items():
                        if not (key in other and other[key] == value):
                            return False
                    return True
            else:
                return self.items() == other.items()

        return self == CaseInsensitiveDict(other)

    def copy(self):
        return CaseInsensitiveDict(self._store)
