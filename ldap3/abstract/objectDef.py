"""
"""

# Created on 2014.02.02
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

from .attrDef import AttrDef
from ..core.exceptions import LDAPKeyError, LDAPObjectError, LDAPAttributeError, LDAPSchemaError
from .. import STRING_TYPES, SEQUENCE_TYPES, Server, Connection
from ..protocol.rfc4512 import SchemaInfo
from ..protocol.formatters.standard import find_attribute_validator
from ..utils.ciDict import CaseInsensitiveDict


class ObjectDef(object):
    """Represent an object in the LDAP server. AttrDefs are stored in a dictionary; the key is the friendly name defined in AttrDef.

    AttrDefs can be added and removed using the += ad -= operators

    ObjectDef can be accessed either as a sequence and a dictionary. When accessed the whole AttrDef instance is returned

    """
    def __init__(self, object_class=None, schema=None, custom_validator=None):
        if object_class is None:
            object_class = []

        if not isinstance(object_class, SEQUENCE_TYPES):
            object_class = [object_class]

        self.__dict__['_attributes'] = CaseInsensitiveDict()
        self.__dict__['_custom_validator'] = custom_validator
        self.__dict__['_oid_info'] = []

        if schema is not None:
            if isinstance(schema, Server):
                schema = schema.schema
            elif isinstance(schema, Connection):
                schema = schema.server.schema
            elif isinstance(schema, SchemaInfo):
                schema = schema
            elif schema:
                raise LDAPSchemaError('unable to read schema')
            if schema is None:
                raise LDAPSchemaError('schema not present')
        self.__dict__['_schema'] = schema

        if self._schema:
            object_class = [schema.object_classes[name].name[0] for name in object_class]  # uses object class names capitalized as in schema
            for object_name in object_class:
                if object_name:
                    self._populate_attr_defs(object_name)

        self.__dict__['_object_class'] = object_class

    def _populate_attr_defs(self, object_name):
        if object_name in self._schema.object_classes:
            object_schema = self._schema.object_classes[object_name]
            self.__dict__['_oid_info'].append(object_name + ' OID: ' + str(object_schema.oid))

            if object_schema.superior:
                for sup in object_schema.superior:
                    self._populate_attr_defs(sup)
            for attribute_name in object_schema.must_contain:
                self.add_from_schema(attribute_name, True)
            for attribute_name in object_schema.may_contain:
                if attribute_name not in self._attributes:  # the attribute could already be definied as "mandatory" in a superclass
                    self.add_from_schema(attribute_name, False)
        else:
            raise LDAPObjectError('object class \'%s\' not defined in schema' % object_name)

    def __repr__(self):
        if self._object_class:
            r = 'OBJ: ' + ', '.join(self._object_class)
        else:
            r = 'OBJ: <None>'
        r += ' [' + ', '.join([oid for oid in self._oid_info]) + ']' + linesep
        # for oid in self._oid_info:
        #     for line in oid.split(linesep):
        #         r += linesep + '  ' + line
        r += 'ATTRS: ' + ', '.join(sorted(self._attributes)) + linesep
        # for attr in sorted(self._attributes):
            # for line in str(self._attributes[attr]).split(linesep):
            #     r += linesep + '  ' + line
        return r

    def __str__(self):
        return self.__repr__()

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __getattr__(self, item):
        item = ''.join(item.split()).lower()
        if '_attributes' in self.__dict__:
            for attr in self.__dict__['_attributes']:
                if item == attr.lower():
                    break
            else:
                raise LDAPKeyError('key \'%s\' not present' % item)

            return self._attributes[attr]

        raise LDAPKeyError('_attributes not defined')

    def __setattr__(self, key, value):
        raise LDAPObjectError('object \'%s\' is read only' % key)

    def __iadd__(self, other):
        self.add_attribute(other)
        return self

    def __isub__(self, other):
        if isinstance(other, AttrDef):
            self.remove_attribute(other.key)
        elif isinstance(other, STRING_TYPES):
            self.remove_attribute(other)

        return self

    def __iter__(self):
        for attribute in self._attributes:
            yield self._attributes[attribute]

    def __len__(self):
        return len(self._attributes)

    if str != bytes:  # python 3
        def __bool__(self):  # needed to make the objectDef appears as existing in "if cursor:" even if there are no entries
            return True
    else:  # python 2
        def __nonzero__(self):
            return True

    def __contains__(self, item):
        try:
            self.__getitem__(item)
        except KeyError:
            return False

        return True

    def add_from_schema(self, attribute_name, mandatory=False):
        attr_def = AttrDef(attribute_name)
        attr_def.validate = find_attribute_validator(self._schema, attribute_name, self._custom_validator)
        attr_def.mandatory = mandatory  # in schema mandatory is specified in the object class, not in the attribute class
        if self._schema:
            if attribute_name in self._schema.attribute_types:
                attr_def.single_value = self._schema.attribute_types[attribute_name].single_value
                attr_def.oid_info = self._schema.attribute_types[attribute_name]
        self.add_attribute(attr_def)

    def add_attribute(self, definition=None):
        """Add an AttrDef to the ObjectDef. Can be called with the += operator.
        :param definition: the AttrDef object to add, can also be a string containing the name of attribute to add. Can be a list of both

        """
        if isinstance(definition, STRING_TYPES):
            self.add_from_schema(definition)
        elif isinstance(definition, AttrDef):
            self._attributes[definition.key] = definition
            if not definition.validate:
                validator = find_attribute_validator(self._schema, definition.key, self._custom_validator)
                self._attributes[definition.key].validate = validator
        elif isinstance(definition, SEQUENCE_TYPES):
            for element in definition:
                self.add_attribute(element)
        else:
            raise LDAPObjectError('unable to add element to object definition')

    def remove_attribute(self, item):
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
            raise LDAPAttributeError('key must be str or AttrDef not ' + str(type(key)))

    def clear_attributes(self):
        """Empty the ObjectDef attribute list

        """
        self.__dict__['object_class'] = None
        self.__dict__['_attributes'] = dict()
