"""
Created on 2014.01.11

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


class AttrDef(object):
    def __init__(self, name, key = None, validate = None, preQuery = None, postQuery = None, default = None, dereferencedObjectDef = None, postQueryReturnsList = False):
        self.name = name
        self.key = ''.join(key.split()) if key else name  # key set to name if not present
        self.validate = validate
        self.preQuery = preQuery
        self.postQuery = postQuery
        self.postQueryReturnsList = postQueryReturnsList
        self.default = default
        self.dereferencedObjectDef = dereferencedObjectDef

    def __repr__(self):
        r = 'AttrDef(name={0.name!r}'.format(self)
        r += '' if self.key is None or self.name == self.key else ', key={0.key!r}'.format(self)
        r += '' if self.validate is None else ', validate={0.validate!r}'.format(self)
        r += '' if self.preQuery is None else ', preQuery={0.preQuery!r}'.format(self)
        r += '' if self.postQuery is None else ', postQuery={0.postQuery!r}'.format(self)
        r += '' if self.default is None else ', default={0.default!r}'.format(self)
        r += ')'

        return r

    def __str__(self):
        return self.__repr__()

    def __eq__(self, other):
        if isinstance(other, AttrDef):
            if self.key == other.key:
                return True

        return False

    def __hash__(self):
        if self.key:
            return hash(self.key)
        else:
            return id(self)  # unique for each istance

    def __setattr__(self, key, value):
        if hasattr(self, 'key') and key == 'key':  # key cannot be changed because is being used for __hash__
            raise Exception('key already set')
        else:
            object.__setattr__(self, key, value)
