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

from .. import SEQUENCE_TYPES, MODIFY_ADD, MODIFY_REPLACE, MODIFY_DELETE
from .attribute import Attribute
from ..core.exceptions import LDAPAttributeError


class WritableAttribute(Attribute):
    # def __setattr__(self, item, value):
    #     raise LDAPAttributeError('attribute \'%s\' is read only, use add_value(), set_value() or delete_value()' % item)

    def __init__(self, attr_def, entry, cursor):
        Attribute.__init__(self, attr_def, entry, cursor)
        self.changes  = []

    def add_value(self, value):
        # new value for attribute to commit with a MODIFY_ADD
        if value is not None and not self.definition.validate(self.definition.name, value):
            raise LDAPAttributeError('value %s non valid for attribute \'%s\'' % (value, self.key))
        self.changes.append((MODIFY_ADD, value if isinstance(value, SEQUENCE_TYPES) else [value]))

    def set_value(self, value):
        # new value for attribute to commit with a MODIFY_REPLACE, old values are deleted
        if value is not None and not self.definition.validate(self.definition.name, value):
            raise LDAPAttributeError('value %s non valid for attribute \'%s\'' % (value, self.key))
        self.changes.append((MODIFY_REPLACE, value if isinstance(value, SEQUENCE_TYPES) else [value]))

    def delete_value(self, value):
        # value for attribute to delete in commit with a MODIFY_DELETE
        if value is not None and not self.definition.validate(self.definition.name, value):
            raise LDAPAttributeError('value %s non valid for attribute \'%s\'' % (value, self.key))
        self.changes.append((MODIFY_DELETE, value if isinstance(value, SEQUENCE_TYPES) else [value]))

    def discard_changes(self):
        self.changes = []
