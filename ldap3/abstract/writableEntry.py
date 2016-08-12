"""
"""

# Created on 2016.08.12
#
# Author: Giovanni Cannata
#
# Copyright 2016 Giovanni Cannata
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

from .. import MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
from .entry import Entry
from .writableAttribute import WritableAttribute
from ..core.exceptions import LDAPEntryError


class WritableEntry(Entry):
    def __setattr__(self, item, value):
        if item in self._reader.definition._attributes:
            if item not in self._attributes:  # adding value to an attribute still without values
                new_attribute = WritableAttribute(self._reader.definition._attributes[item], self, reader=self._reader)
                new_attribute.__dict__['_response'] = None
                new_attribute.__dict__['raw_values'] = None
                new_attribute.__dict__['values'] = None
                self._attributes[item] = new_attribute
            self._attributes[item].set_value(value)  # try to add to new_values
        else:
            raise LDAPEntryError('attribute \'%s\' not allowed' % item)

    def entry_commit(self, controls=None):
        changes = dict()
        for key in self._attributes:
            attribute = self._attributes[key]
            change = []
            if 'values_to_replace' in attribute.__dict__:
                change.append((MODIFY_REPLACE, attribute.values_to_replace))
            if 'values_to_add' in attribute.__dict__:
                change.append((MODIFY_ADD, attribute.values_to_add))
            if 'values_to_delete' in attribute.__dict__:
                change.append((MODIFY_DELETE, attribute.values_to_delete))
            if change:
                changes[attribute.definition.name] = change

        if changes:
            if self._reader.connection.modify(self._dn, changes, controls):
                self.entry_refresh()
            else:
                raise LDAPEntryError('unable to commit entry')
