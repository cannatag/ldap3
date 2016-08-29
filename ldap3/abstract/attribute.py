"""
"""

# Created on 2014.01.06
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
from .. import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE, SEQUENCE_TYPES
from ..core.exceptions import LDAPAttributeError
from ..utils.repr import to_stdout_encoding


# noinspection PyUnresolvedReferences
class Attribute(object):
    """Attribute/values object, it includes the search result (after post_query transformation) of each attribute in an entry

    Attribute object is read only

    - values: contain the processed attribute values
    - raw_values': contain the unprocessed attribute values


    """

    def __init__(self, attr_def, entry, cursor):
        self.key = attr_def.key
        self.definition = attr_def
        self.values = []
        self.raw_values = []
        self.response = None
        self.entry = entry
        self.cursor = cursor

    def __repr__(self):
        if len(self.values) == 1:
            r = self.key + ': ' + to_stdout_encoding(self.values[0])
        elif len(self.values) > 1:
            r = self.key + ': ' + to_stdout_encoding(self.values[0])
            filler = ' ' * (len(self.key) + 6)
            for value in self.values[1:]:
                r += linesep + filler + to_stdout_encoding(value)
        else:
            r = self.key + ': ' + to_stdout_encoding('<no value>')

        return r

    def __str__(self):
        if len(self.values) == 1:
            return to_stdout_encoding(self.values[0])
        else:
            return to_stdout_encoding(self.values)

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return self.values.__iter__()

    def __getitem__(self, item):
        return self.values[item]

    def __eq__(self, other):
        try:
            if self.value == other:
                return True
        except:
            return False

    @property
    def value(self):
        """
        :return: The single value or a list of values of the attribute.
        """
        return self.values[0] if len(self.values) == 1 else self.values


class OperationalAttribute(Attribute):
    """Operational attribute/values object. Include the search result of an
    operational attribute in an entry

    OperationalAttribute object is read only

    - values: contains the processed attribute values
    - raw_values: contains the unprocessed attribute values

    It may not have an AttrDef

    """

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


class WritableAttribute(Attribute):
    def __init__(self, attr_def, entry, cursor):
        Attribute.__init__(self, attr_def, entry, cursor)
        self.changes  = []

    def __repr__(self):
        filler = ' ' * (len(self.key) + 6)
        if len(self.values) == 1:
            r = self.key + ': ' + to_stdout_encoding(self.values[0])
        elif len(self.values) > 1:
            r = self.key + ': ' + to_stdout_encoding(self.values[0])
            for value in self.values[1:]:
                r += linesep + filler + to_stdout_encoding(value)
        else:
            r = self.key + ': ' + to_stdout_encoding('<None>')
        if self.changes:
            r += linesep + filler + 'CHANGES: ' + str(self.changes)
        return r

    def __iadd__(self, other):
        self.add_value(other)
        return Ellipsis  # hack to avoid calling set_value in entry __setattr__

    def __isub__(self, other):
        self.delete_value(other)
        return Ellipsis  # hack to avoid calling set_value in entry __setattr__

    def add_value(self, value):
        # new value for attribute to commit with a MODIFY_ADD
        if value is None:
            raise LDAPAttributeError('added value cannot be None')
        # if self.values and self.definition.single_value:
        #    raise LDAPAttributeError("can't add to a single value attributewith already a value, use set_value")
        if value is not None and not self.definition.validate(self.definition.name, value):
            raise LDAPAttributeError('value \'%s\' non valid for attribute \'%s\'' % (value, self.key))
        self.changes.append((MODIFY_ADD, value if isinstance(value, SEQUENCE_TYPES) else [value]))

    def set_value(self, value):
        # new value for attribute to commit with a MODIFY_REPLACE, old values are deleted
        if value is None:
            raise LDAPAttributeError('new value cannot be None')
        if not self.definition.validate(self.definition.name, value):
            raise LDAPAttributeError('value \'%s\' non valid for attribute \'%s\'' % (value, self.key))
        self.changes.append((MODIFY_REPLACE, value if isinstance(value, SEQUENCE_TYPES) else [value]))

    def delete_value(self, value):
        # value for attribute to delete in commit with a MODIFY_DELETE
        if value is None:
            raise LDAPAttributeError('value to delete cannot be None')

        if value in self.values:
            if not self.definition.validate(self.definition.name, value):
                raise LDAPAttributeError('value \'%s\' non valid for attribute \'%s\'' % (value, self.key))
        else:
            raise LDAPAttributeError('value \'%s\' not present in \'%s\'' % (value, self.values))
        self.changes.append((MODIFY_DELETE, value if isinstance(value, SEQUENCE_TYPES) else [value]))

    def discard_changes(self):
        self.changes = []

#
