"""
"""

# Created on 2014.02.02
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2016 Giovanni Cannata
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

from .attrDef import AttrDef
from ..core.exceptions import LDAPKeyError, LDAPObjectError, LDAPAttributeError, LDAPTypeError, LDAPSchemaError
from .. import STRING_TYPES, SEQUENCE_TYPES, Server, Connection
from ..protocol.rfc4512 import SchemaInfo

class ObjectDef(object):
    """Represent an object in the LDAP server. AttrDefs are stored in a dictionary; the key is the friendly name defined in AttrDef.

    AttrDefs can be added and removed using the += ad -= operators

    ObjectDef can be accessed either as a sequence and a dictionary. When accessed the whole AttrDef instance is returned

    """
    def __init__(self, object_class=None, schema=None):
        self.__dict__['object_class'] = object_class
        self.__dict__['_attributes'] = dict()
        if isinstance(schema, Server):
            schema = schema.schema
        elif isinstance(schema, Connection):
            schema = schema.server.schema
        elif isinstance(schema, SchemaInfo):
            schema = schema
        elif schema:
            raise LDAPSchemaError('unable to read schema')

        if schema:
            if not isinstance(object_class, SEQUENCE_TYPES):
                object_class = [object_class]

            for element in object_class:
                if element in schema.object_classes:
                    for attribute_type in schema.object_classes[element].must_contain:
                        self.add(attribute_type, schema)
                    for attribute_type in schema.object_classes[element].may_contain:
                        self.add(attribute_type, schema)

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
            raise LDAPKeyError('key \'%s\' not present' % item)

        return self._attributes[attr]

    def __setattr__(self, key, value):
        raise LDAPObjectError('object \'%s\' is read only' % key)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __isub__(self, other):
        if isinstance(other, AttrDef):
            self.remove(other.key)
        elif isinstance(other, STRING_TYPES):
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
        except KeyError:
            return False

        return True

    def add(self, definition=None, schema=None):
        """Add an AttrDef to the ObjectDef. Can be called with the += operator.
        :param definition: the AttrDef object to add, can also be a string containing the name of attribute to add

        """

        if isinstance(definition, STRING_TYPES):
            element = AttrDef(definition, validate_input=True if schema else False)
            self.add(element)
        elif isinstance(definition, AttrDef):
            key = definition.key
            for attr in self._attributes:
                if key.lower() == attr.lower():
                    pass
                    # raise LDAPAttributeError('attribute \'%s\' already present' % key)
            self._attributes[key] = definition
            self.__dict__[key] = definition
        elif isinstance(definition, SEQUENCE_TYPES):
            for element in definition:
                self.add(element, schema)
        else:
            raise LDAPObjectError('unable to add element to object definition')

    def remove(self, item):
        """Remove an AttrDef from the ObjectDef. Can be called with the -= operator.
        :param item: the AttrDef to remove, can also be a string containing the name of attribute to remove

        """
        key = None
        if isinstance(item, STRING_TYPES):
            key = ''.join(item.split()).lower()
        elif isinstance(item, AttrDef):
            key = item.key

        if key:
            for attr in self._attributes:
                if item == attr.lower():
                    del self._attributes[attr]
                    break
            else:
                raise LDAPKeyError('key \'%s\' not present' % key)
        else:
            raise LDAPTypeError('key must be str or AttrDef not '
                                + str(type(key)))

    def clear(self):
        """Empty the ObjectDef attribute list

        """
        self.__dict__['object_class'] = None
        self.__dict__['_attributes'] = dict()
