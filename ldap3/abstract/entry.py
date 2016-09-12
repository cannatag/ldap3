"""
"""

# Created on 2016.08.19
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


import json
try:
    from collections import OrderedDict
except ImportError:
    from ..utils.ordDict import OrderedDict  # for Python 2.6

from os import linesep
from copy import copy, deepcopy

from .. import STRING_TYPES, SEQUENCE_TYPES

from .attribute import WritableAttribute
from .objectDef import ObjectDef
from ..core.exceptions import LDAPKeyError, LDAPCursorError
from ..utils.conv import check_json_dict, format_json, prepare_for_stream
from ..protocol.rfc2849 import operation_to_ldif, add_ldif_header
from ..utils.repr import to_stdout_encoding
from ..utils.ciDict import CaseInsensitiveDict
from . import STATUS_VIRTUAL, STATUS_WRITABLE, STATUS_PENDING_CHANGES, STATUS_COMMITTED, STATUS_DELETED, STATUS_INIT, STATUS_READY_FOR_DELETION, STATUS_MANDATORY_MISSING, STATUSES, INITIAL_STATUSES


class EntryState(object):
    """Contains data on the status of the entry. Does not pollute the Entry __dict__.

    """

    def __init__(self, dn, cursor):
        self.dn = dn
        self._initial_status = None
        self.status = STATUS_INIT
        self.attributes = CaseInsensitiveDict()
        self.raw_attributes = CaseInsensitiveDict()
        self.response = None
        self.cursor = cursor
        self.origin = None  # reference to the original read-only entry (set when made writable). Needed to update attributes in read-only when modified
        self.read_time = None
        self.changes = OrderedDict()  # includes changes to commit in a writable entry
        if cursor.definition:
            self.definition = cursor.definition
        else:
            self.definition = None

    def __repr__(self):
        if self.__dict__ and self.dn is not None:
            r = 'DN: ' + to_stdout_encoding(self.dn) + ' - STATUS: ' + ((self._initial_status + ', ') if self._initial_status != self.status else '') + self.status + ' - READ TIME: ' + (self.read_time.isoformat() if self.read_time else '<never>') + linesep
            r += 'attributes: ' + ', '.join(sorted(self.attributes.keys())) + linesep
            r += 'object def: ' + (', '.join(sorted(self.definition._object_class)) if self.definition._object_class else '<None>') + linesep
            r += 'attr defs: ' + ', '.join(sorted(self.definition._attributes.keys())) + linesep
            r += 'response: ' + ('present' if self.response else '<None>') + linesep
            r += 'cursor: ' + (self.cursor.__class__.__name__ if self.cursor else '<None>') + linesep
            return r
        else:
            return object.__repr__(self)

    def __str__(self):
        return self.__repr__()

    def set_status(self, status):
        if status not in STATUSES:
            raise LDAPCursorError('invalid entry status ' + str(status))

        if status in INITIAL_STATUSES:
            self._initial_status = status
        self.status = status
        if status == STATUS_DELETED:
            self._initial_status = STATUS_VIRTUAL
        if status == STATUS_COMMITTED:
            self._initial_status = STATUS_WRITABLE
        if self.status == STATUS_VIRTUAL or (self.status == STATUS_PENDING_CHANGES and self._initial_status == STATUS_VIRTUAL):  # checks if all mandatory attributes are present in new entries
            for attr in self.definition._attributes:
                if self.definition._attributes[attr].mandatory:
                    if (attr not in self.attributes or self.attributes[attr].virtual) and attr not in self.changes:
                        self.status = STATUS_MANDATORY_MISSING
                        break


class EntryBase(object):
    """The Entry object contains a single LDAP entry.
    Attributes can be accessed either by sequence, by assignment
    or as dictionary keys. Keys are not case sensitive.

    The Entry object is read only

    - The DN is retrieved by _dn
    - The cursor reference is in _cursor
    - Raw attributes values are retrieved with _raw_attributes and the _raw_attribute() methods
    """

    def __init__(self, dn, cursor):
        self.__dict__['_state'] = EntryState(dn, cursor)

    def __repr__(self):
        if self.__dict__ and self._dn is not None:
            r = 'DN: ' + to_stdout_encoding(self._dn) + ' - STATUS: ' + ((self._state._initial_status + ', ') if self._state._initial_status != self._status else '') + self._status + ' - READ TIME: ' + (self._read_time.isoformat() if self._read_time else '<never>') + linesep
            if self._state.attributes:
                for attr in sorted(self._state.attributes):
                    r += ' ' * 4 + repr(self._state.attributes[attr]) + linesep
            return r
        else:
            return object.__repr__(self)

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        for attribute in self._state.attributes:
            yield self._state.attributes[attribute]
        raise StopIteration

    def __contains__(self, item):
        try:
            self.__getitem__(item)
            return True
        except LDAPKeyError:
            return False

    def __getattr__(self, item):
        if isinstance(item, STRING_TYPES):
            if item == '_state':
                return self.__dict__['_state']
            item = ''.join(item.split()).lower()
            for attr in self._state.attributes.keys():
                if item == attr.lower():
                    break
            else:
                raise LDAPCursorError('attribute \'%s\' not found' % item)
            return self._state.attributes[attr]

        raise LDAPCursorError('attribute name must be a string')

    def __setattr__(self, item, value):
        if item in self._state.attributes:
            raise LDAPCursorError('attribute \'%s\' is read only' % item)
        else:
            raise LDAPCursorError('entry \'%s\' is read only' % item)

    def __getitem__(self, item):
        if isinstance(item, STRING_TYPES):
            item = ''.join(item.split()).lower()
            for attr in self._state.attributes.keys():
                if item == attr.lower():
                    break
            else:
                raise LDAPKeyError('key \'%s\' not found' % item)
            return self._state.attributes[attr]

        raise LDAPKeyError('key must be a string')

    def __eq__(self, other):
        if isinstance(other, EntryBase):
            return self._dn == other._dn

        return False

    def __lt__(self, other):
        if isinstance(other, EntryBase):
            return self._dn <= other._dn

        return False

    @property
    def _dn(self):
        return self._state.dn

    @property
    def _cursor(self):
        return self._state.cursor

    @property
    def _status(self):
        return self._state.status

    @property
    def _definition(self):
        return self._state.definition

    @property
    def _raw_attributes(self):
        return self._state.raw_attributes

    def _get_raw_attribute(self, name):
        """

        :param name: name of the attribute
        :return: raw (unencoded) value of the attribute, None if attribute is not found
        """
        return self._state.raw_attributes[name] if name in self._state.raw_attributes else None

    @property
    def _mandatory(self):
        return [attribute for attribute in self._definition._attributes if self._definition._attributes[attribute].mandatory]

    @property
    def _attributes(self):
        return list(self._state.attributes.keys())

    @property
    def _attributes_as_dict(self):
        return dict((attribute_key, attribute_value.values) for (attribute_key, attribute_value) in self._state.attributes.items())

    @property
    def _read_time(self):
        return self._state.read_time

    @property
    def _changes(self):
        return self._state.changes

    def _to_json(self, raw=False, indent=4, sort=True, stream=None, checked_attributes=True):
        json_entry = dict()
        json_entry['dn'] = self._dn
        if checked_attributes:
            json_entry['attributes'] = self._attributes_as_dict
        if raw:
            json_entry['raw'] = dict(self._raw_attributes)

        if str == bytes:
            check_json_dict(json_entry)

        json_output = json.dumps(json_entry,
                                 ensure_ascii=True,
                                 sort_keys=sort,
                                 indent=indent,
                                 check_circular=True,
                                 default=format_json,
                                 separators=(',', ': '))

        if stream:
            stream.write(json_output)

        return json_output

    def entry_to_json(self,  # compatibility for version < 2.0.0 outside of the abstract namespae
                      raw=False,
                      indent=4,
                      sort=True,
                      stream=None,
                      checked_attributes=True):
        return self._to_json(raw, indent, sort, stream, checked_attributes)

    def _to_ldif(self, all_base64=False, line_separator=None, sort_order=None, stream=None):
        ldif_lines = operation_to_ldif('searchResponse', [self._response], all_base64, sort_order=sort_order)
        ldif_lines = add_ldif_header(ldif_lines)
        line_separator = line_separator or linesep
        ldif_output = line_separator.join(ldif_lines)
        if stream:
            if stream.tell() == 0:
                header = add_ldif_header(['-'])[0]
                stream.write(prepare_for_stream(header + line_separator + line_separator))
            stream.write(prepare_for_stream(ldif_output + line_separator + line_separator))
        return ldif_output

    def entry_to_ldif(self, all_base64=False, line_separator=None, sort_order=None, stream=None):
        return self._to_ldif(all_base64, line_separator, sort_order, stream)


class Entry(EntryBase):
    """The Entry object contains a single LDAP entry.
    Attributes can be accessed either by sequence, by assignment
    or as dictionary keys. Keys are not case sensitive.

    The Entry object is read only

    - The DN is retrieved by _dn()
    - The Reader reference is in _cursor()
    - Raw attributes values are retrieved by the _ra_attributes and
      _raw_attribute() methods

    """
    def _writable(self, object_def=None, writer_cursor=None, attributes=None, custom_validator=None):
        if not self._cursor.schema:
            raise LDAPCursorError('The schema must be available to make an entry writable')
        # returns a newly created WritableEntry and its relevant Writer
        if object_def is None:
            if self._cursor.definition._object_class:
                object_def = self._cursor.definition._object_class
            elif 'objectclass' in self:
                object_def = self.objectclass.values

        if not object_def:
            raise LDAPCursorError('object class must be specified to make an entry writable')

        if not isinstance(object_def, ObjectDef):
                object_def = ObjectDef(object_def, self._cursor.schema, custom_validator)

        if attributes:
            if isinstance(attributes, STRING_TYPES):
                attributes = [attributes]

            if isinstance(attributes, SEQUENCE_TYPES):
                for attribute in attributes:
                    if attribute not in object_def._attributes:
                        raise LDAPCursorError('attribute \'%s\' not in schema for \'%s\'' % (attribute, object_def))
        else:
            attributes = []

        if not writer_cursor:
            from .cursor import Writer  # local import to avoid circular reference in import at startup
            writable_cursor = Writer(self._cursor.connection, object_def)
        else:
            writable_cursor = writer_cursor

        if attributes:  # force reading of attributes
            writable_entry = writable_cursor._refresh_object(self._dn, list(attributes) + self._attributes)
        else:
            writable_entry = writable_cursor._create_entry(deepcopy(self._state.response))
            writable_cursor.entries.append(writable_entry)
            writable_entry._state.read_time = copy(self._read_time)
        writable_entry._state.origin = self  # reference to the original read-only entry
        writable_entry._state.set_status(STATUS_WRITABLE)
        return writable_entry


class WritableEntry(EntryBase):
    def __setattr__(self, item, value):
        if item == '_state' and isinstance(value, EntryState):
            self.__dict__['_state'] = value
            return

        if value is not Ellipsis:  # hack for using implicit operators in writable attributes
            if item in self._cursor.definition._attributes:
                if item not in self._state.attributes:  # setting value to an attribute still without values
                    new_attribute = WritableAttribute(self._cursor.definition._attributes[item], self, cursor=self._cursor)
                    self._state.attributes[str(item)] = new_attribute  # force item to a string for key in attributes dict
                self._state.attributes[item].set(value)  # try to add to new_values
            else:
                raise LDAPCursorError('attribute \'%s\' not defined' % item)

    def __getattr__(self, item):
        if isinstance(item, STRING_TYPES):
            if item == '_state':
                return self.__dict__['_state']
            item = ''.join(item.split()).lower()
            for attr in self._state.attributes.keys():
                if item == attr.lower():
                    return self._state.attributes[attr]
            if item in self._definition._attributes:  # item is a new attribute to commit, creates the AttrDef and add to the attributes to retrive
                self._state.attributes[item] = WritableAttribute(self._definition._attributes[item], self, self._cursor)
                self._cursor.attributes.add(item)
                return self._state.attributes[item]
            # if item in self._definition._attributes:
            #     raise LDAPCursorError('attribute must have a value')
            raise LDAPCursorError('attribute \'%s\' is not defined' % item)
        else:
            raise LDAPCursorError('attribute must be a string')

    def _commit(self, refresh=True, controls=None):
        if self._status == STATUS_READY_FOR_DELETION:
            origin = None
            if self._cursor.connection.delete(self._dn, controls):
                dn = self._dn
                if self._state.origin:  # deletes original read-only entry if present
                    cursor = self._state.origin._cursor
                    self._state.origin.__dict__.clear()
                    self._state.origin.__dict__['_state'] = EntryState(dn, cursor)
                    origin = self._state.origin
                cursor = self._cursor
                self.__dict__.clear()
                self._state = EntryState(dn, cursor)
                self._state.origin = origin
                self._state.set_status(STATUS_DELETED)
                return True
            else:
                raise LDAPCursorError('unable to delete entry, ' + self._state.cursor.connection.result['description'])
        elif self._status in [STATUS_VIRTUAL, STATUS_MANDATORY_MISSING]:
            missing_attributes = []
            for attr in self._mandatory:
                if (attr not in self._state.attributes or self._state.attributes[attr].virtual) and attr not in self._changes:
                    missing_attributes.append('\'' + attr + '\'')
            raise LDAPCursorError('mandatory attributes %s missing in entry %s' % (', '.join(missing_attributes), self._dn))
        elif self._status == STATUS_PENDING_CHANGES:
            if self._changes:
                if self._state._initial_status == STATUS_VIRTUAL:
                    new_attributes = dict()
                    for attr in self._changes:
                        new_attributes[attr] = self._changes[attr][0][1]
                    result = self._cursor.connection.add(self._dn, None, new_attributes, controls)
                else:
                    result = self._cursor.connection.modify(self._dn, self._changes, controls)
                if result:
                    if refresh:
                        self._refresh()
                        origin = self._state.origin
                        if origin:  # updates original read-only entry if present
                            for attr in self:  # adds AttrDefs from writable entry to origin entry definition if some is missing
                                if attr.key in self._definition._attributes and attr.key not in origin._definition._attributes:
                                    origin._cursor.definition.add(self._cursor.definition._attributes[attr.key])  # adds AttrDef from writable entry to original entry if missing
                            temp_entry = origin._cursor._create_entry(deepcopy(self._state.response))
                            origin.__dict__.clear()
                            origin.__dict__['_state'] = temp_entry._state
                            for attr in self:  # returns the whole attribute object
                                if not attr.virtual:
                                    origin.__dict__[attr.key] = origin._state.attributes[attr.key]
                            origin._state.read_time = copy(self._read_time)
                    self._state.set_status(STATUS_COMMITTED)
                    return True
                else:
                    raise LDAPCursorError('unable to commit entry, ' + self._cursor.connection.result['description'] + ' - ' + self._cursor.connection.result['message'])
        return False

    def _discard(self):
        self._changes.clear()
        self._state.set_status(self._state._initial_status)

    def _delete(self):
        if self._status not in [STATUS_WRITABLE, STATUS_COMMITTED, STATUS_READY_FOR_DELETION]:
            raise LDAPCursorError('unable to delete entry, invalid status: ' + self._status)

        self._state.set_status(STATUS_READY_FOR_DELETION)

    def _refresh(self):
        """

        Read the entry from the LDAP Server
        """
        if self._cursor.connection:
            self._cursor.refresh_entry(self)
            return True
        return False

    def _move(self, destination_dn):
        raise NotImplementedError

    def _rename(self):
        raise NotImplementedError
