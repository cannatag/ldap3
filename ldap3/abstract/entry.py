"""
"""

# Created on 2016.08.19
#
# Author: Giovanni Cannata
#
# Copyright 2016, 2017 Giovanni Cannata
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

from .. import STRING_TYPES, SEQUENCE_TYPES
from .attribute import WritableAttribute
from .objectDef import ObjectDef
from ..core.exceptions import LDAPKeyError, LDAPCursorError
from ..utils.conv import check_json_dict, format_json, prepare_for_stream
from ..protocol.rfc2849 import operation_to_ldif, add_ldif_header
from ..utils.dn import safe_dn, safe_rdn, to_dn
from ..utils.repr import to_stdout_encoding
from ..utils.ciDict import CaseInsensitiveWithAliasDict
from ..utils.config import get_config_parameter
from . import STATUS_VIRTUAL, STATUS_WRITABLE, STATUS_PENDING_CHANGES, STATUS_COMMITTED, STATUS_DELETED,\
    STATUS_INIT, STATUS_READY_FOR_DELETION, STATUS_READY_FOR_MOVING, STATUS_READY_FOR_RENAMING, STATUS_MANDATORY_MISSING, STATUSES, INITIAL_STATUSES
from ..core.results import RESULT_SUCCESS


class EntryState(object):
    """Contains data on the status of the entry. Does not pollute the Entry __dict__.

    """

    def __init__(self, dn, cursor):
        self.dn = dn
        self._initial_status = None
        self._to = None  # used for move and rename
        self.status = STATUS_INIT
        self.attributes = CaseInsensitiveWithAliasDict()
        self.raw_attributes = CaseInsensitiveWithAliasDict()
        self.response = None
        self.cursor = cursor
        self.origin = None  # reference to the original read-only entry (set when made writable). Needed to update attributes in read-only when modified (only if both refer the same server)
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
        conf_ignored_mandatory_attributes_in_object_def = [v.lower() for v in get_config_parameter('IGNORED_MANDATORY_ATTRIBUTES_IN_OBJECT_DEF')]
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
                if self.definition._attributes[attr].mandatory and attr.lower() not in conf_ignored_mandatory_attributes_in_object_def:
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
        if self.__dict__ and self.entry_dn is not None:
            r = 'DN: ' + to_stdout_encoding(self.entry_dn) + ' - STATUS: ' + ((self._state._initial_status + ', ') if self._state._initial_status != self.entry_status else '') + self.entry_status + ' - READ TIME: ' + (self.entry_read_time.isoformat() if self.entry_read_time else '<never>') + linesep
            if self._state.attributes:
                for attr in sorted(self._state.attributes):
                    if self._state.attributes[attr] or (hasattr(self._state.attributes[attr], 'changes') and self._state.attributes[attr].changes):
                        r += '    ' + repr(self._state.attributes[attr]) + linesep
            return r
        else:
            return object.__repr__(self)

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        for attribute in self._state.attributes:
            yield self._state.attributes[attribute]
        # raise StopIteration  # deprecated in PEP 479
        return

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
            attr_found = None
            for attr in self._state.attributes.keys():
                if item == attr.lower():
                    attr_found = attr
                    break
            if not attr_found:
                for attr in self._state.attributes.aliases():
                    if item == attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                for attr in self._state.attributes.keys():
                    if item + ';binary' == attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                for attr in self._state.attributes.aliases():
                    if item + ';binary' == attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                for attr in self._state.attributes.keys():
                    if item + ';range' in attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                for attr in self._state.attributes.aliases():
                    if item + ';range' in attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
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
            attr_found = None
            for attr in self._state.attributes.keys():
                if item == attr.lower():
                    attr_found = attr
                    break
            if not attr_found:
                for attr in self._state.attributes.aliases():
                    if item == attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                for attr in self._state.attributes.keys():
                    if item + ';binary' == attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                for attr in self._state.attributes.aliases():
                    if item + ';binary' == attr.lower():
                        attr_found = attr
                        break
            if not attr_found:
                raise LDAPKeyError('key \'%s\' not found' % item)
            return self._state.attributes[attr]

        raise LDAPKeyError('key must be a string')

    def __eq__(self, other):
        if isinstance(other, EntryBase):
            return self.entry_dn == other.entry_dn

        return False

    def __lt__(self, other):
        if isinstance(other, EntryBase):
            return self.entry_dn <= other.entry_dn

        return False

    @property
    def entry_dn(self):
        return self._state.dn

    @property
    def entry_cursor(self):
        return self._state.cursor

    @property
    def entry_status(self):
        return self._state.status

    @property
    def entry_definition(self):
        return self._state.definition

    @property
    def entry_raw_attributes(self):
        return self._state.entry_raw_attributes

    def entry_raw_attribute(self, name):
        """

        :param name: name of the attribute
        :return: raw (unencoded) value of the attribute, None if attribute is not found
        """
        return self._state.entry_raw_attributes[name] if name in self._state.entry_raw_attributes else None

    @property
    def entry_mandatory_attributes(self):
        return [attribute for attribute in self.entry_definition._attributes if self.entry_definition._attributes[attribute].mandatory]

    @property
    def entry_attributes(self):
        # attr_list = list()
        # for attr in self._state.attributes:
        #     if self._state.definition[attr].name:
        #         attr_list.append(self._state.definition[attr].name)
        #     else:
        #         attr_list.append(self._state.definition[attr].key)
        # return attr_list
        return list(self._state.attributes.keys())

    @property
    def entry_attributes_as_dict(self):
        return dict((attribute_key, attribute_value.values) for (attribute_key, attribute_value) in self._state.attributes.items())

    @property
    def entry_read_time(self):
        return self._state.read_time

    @property
    def _changes(self):
        return self._state.changes

    def entry_to_json(self, raw=False, indent=4, sort=True, stream=None, checked_attributes=True, include_empty=True):
        json_entry = dict()
        json_entry['dn'] = self.entry_dn
        if checked_attributes:
            if not include_empty:
                # needed for python 2.6 compatibility
                json_entry['attributes'] = dict((key, self.entry_attributes_as_dict[key]) for key in self.entry_attributes_as_dict if self.entry_attributes_as_dict[key])
            else:
                json_entry['attributes'] = self.entry_attributes_as_dict
        if raw:
            if not include_empty:
                # needed for python 2.6 compatibility
                json_entry['raw'] = dict((key, self.entry_raw_attributes[key]) for key in self.entry_raw_attributes if self.entry_raw_attributes[key])
            else:
                json_entry['raw'] = dict(self.entry_raw_attributes)

        if str is bytes:  # Python 2
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

    def entry_to_ldif(self, all_base64=False, line_separator=None, sort_order=None, stream=None):
        ldif_lines = operation_to_ldif('searchResponse', [self._state.response], all_base64, sort_order=sort_order)
        ldif_lines = add_ldif_header(ldif_lines)
        line_separator = line_separator or linesep
        ldif_output = line_separator.join(ldif_lines)
        if stream:
            if stream.tell() == 0:
                header = add_ldif_header(['-'])[0]
                stream.write(prepare_for_stream(header + line_separator + line_separator))
            stream.write(prepare_for_stream(ldif_output + line_separator + line_separator))
        return ldif_output


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
    def entry_writable(self, object_def=None, writer_cursor=None, attributes=None, custom_validator=None):
        if not self.entry_cursor.schema:
            raise LDAPCursorError('schema must be available to make an entry writable')
        # returns a new WritableEntry and its Writer cursor
        if object_def is None:
            if self.entry_cursor.definition._object_class:
                object_def = self.entry_cursor.definition._object_class
            elif 'objectclass' in self:
                object_def = self.objectclass.values

        if not object_def:
            raise LDAPCursorError('object class must be specified to make an entry writable')

        if not isinstance(object_def, ObjectDef):
                object_def = ObjectDef(object_def, self.entry_cursor.schema, custom_validator)

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
            writable_cursor = Writer(self.entry_cursor.connection, object_def)
        else:
            writable_cursor = writer_cursor

        if attributes:  # force reading of attributes
            writable_entry = writable_cursor._refresh_object(self.entry_dn, list(attributes) + self.entry_attributes)
        else:
            writable_entry = writable_cursor._create_entry(self._state.response)
            writable_cursor.entries.append(writable_entry)
            writable_entry._state.read_time = self.entry_read_time
        writable_entry._state.origin = self  # reference to the original read-only entry
        writable_entry._state.set_status(STATUS_WRITABLE)
        return writable_entry


class WritableEntry(EntryBase):
    def __setitem__(self, key, value):
        if value is not Ellipsis:  # hack for using implicit operators in writable attributes
            self.__setattr__(key, value)

    def __setattr__(self, item, value):
        if item == '_state' and isinstance(value, EntryState):
            self.__dict__['_state'] = value
            return

        if value is not Ellipsis:  # hack for using implicit operators in writable attributes
            if item in self.entry_cursor.definition._attributes:
                if item not in self._state.attributes:  # setting value to an attribute still without values
                    new_attribute = WritableAttribute(self.entry_cursor.definition._attributes[item], self, cursor=self.entry_cursor)
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
            for attr in self._state.attributes.aliases():
                if item == attr.lower():
                    return self._state.attributes[attr]
            if item in self.entry_definition._attributes:  # item is a new attribute to commit, creates the AttrDef and add to the attributes to retrive
                self._state.attributes[item] = WritableAttribute(self.entry_definition._attributes[item], self, self.entry_cursor)
                self.entry_cursor.attributes.add(item)
                return self._state.attributes[item]
            raise LDAPCursorError('attribute \'%s\' not defined' % item)
        else:
            raise LDAPCursorError('attribute name must be a string')

    @property
    def entry_virtual_attributes(self):
        return [attr for attr in self.entry_attributes if self[attr].virtual]

    def entry_commit_changes(self, refresh=True, controls=None, clear_history=True):
        if clear_history:
            self.entry_cursor._reset_history()

        if self.entry_status == STATUS_READY_FOR_DELETION:
            result = self.entry_cursor.connection.delete(self.entry_dn, controls)
            if not self.entry_cursor.connection.strategy.sync:
                response, result, request = self.entry_cursor.connection.get_response(result, get_request=True)
            else:
                response = self.entry_cursor.connection.response
                result = self.entry_cursor.connection.result
                request = self.entry_cursor.connection.request
            self.entry_cursor._store_operation_in_history(request, result, response)
            if result['result'] == RESULT_SUCCESS:
                dn = self.entry_dn
                if self._state.origin and self.entry_cursor.connection.server == self._state.origin.entry_cursor.connection.server:  # deletes original read-only Entry
                    cursor = self._state.origin.entry_cursor
                    self._state.origin.__dict__.clear()
                    self._state.origin.__dict__['_state'] = EntryState(dn, cursor)
                    self._state.origin._state.set_status(STATUS_DELETED)
                cursor = self.entry_cursor
                self.__dict__.clear()
                self._state = EntryState(dn, cursor)
                self._state.set_status(STATUS_DELETED)
                return True

            # raise LDAPCursorError('unable to delete entry, ' + result['description'] + ', ' + result['message'])
            return False
        elif self.entry_status == STATUS_READY_FOR_MOVING:
            result = self.entry_cursor.connection.modify_dn(self.entry_dn, '+'.join(safe_rdn(self.entry_dn)), new_superior=self._state._to)
            if not self.entry_cursor.connection.strategy.sync:
                response, result, request = self.entry_cursor.connection.get_response(result, get_request=True)
            else:
                response = self.entry_cursor.connection.response
                result = self.entry_cursor.connection.result
                request = self.entry_cursor.connection.request
            self.entry_cursor._store_operation_in_history(request, result, response)
            if result['result'] == RESULT_SUCCESS:
                self._state.dn = safe_dn('+'.join(safe_rdn(self.entry_dn)) + ',' + self._state._to)
                if refresh:
                    if self.entry_refresh():
                        if self._state.origin and self.entry_cursor.connection.server == self._state.origin.entry_cursor.connection.server:  # refresh dn of origin
                            self._state.origin._state.dn = self.entry_dn
                self._state.set_status(STATUS_COMMITTED)
                self._state._to = None
                return True
            # raise LDAPCursorError('unable to move entry, ' + result['description'])
            return False
        elif self.entry_status == STATUS_READY_FOR_RENAMING:
            rdn = '+'.join(safe_rdn(self._state._to))
            result = self.entry_cursor.connection.modify_dn(self.entry_dn, rdn)
            if not self.entry_cursor.connection.strategy.sync:
                response, result, request = self.entry_cursor.connection.get_response(result, get_request=True)
            else:
                response = self.entry_cursor.connection.response
                result = self.entry_cursor.connection.result
                request = self.entry_cursor.connection.request
            self.entry_cursor._store_operation_in_history(request, result, response)
            if result['result'] == RESULT_SUCCESS:
                self._state.dn = rdn + ',' + ','.join(to_dn(self.entry_dn)[1:])
                if refresh:
                    if self.entry_refresh():
                        if self._state.origin and self.entry_cursor.connection.server == self._state.origin.entry_cursor.connection.server:  # refresh dn of origin
                            self._state.origin._state.dn = self.entry_dn
                self._state.set_status(STATUS_COMMITTED)
                self._state._to = None
                return True
            # raise LDAPCursorError('unable to move entry, ' + result['description'])
            return False
        elif self.entry_status in [STATUS_VIRTUAL, STATUS_MANDATORY_MISSING]:
            missing_attributes = []
            for attr in self.entry_mandatory_attributes:
                if (attr not in self._state.attributes or self._state.attributes[attr].virtual) and attr not in self._changes:
                    missing_attributes.append('\'' + attr + '\'')
            raise LDAPCursorError('mandatory attributes %s missing in entry %s' % (', '.join(missing_attributes), self.entry_dn))
        elif self.entry_status == STATUS_PENDING_CHANGES:
            if self._changes:
                if self._state._initial_status == STATUS_VIRTUAL:
                    new_attributes = dict()
                    for attr in self._changes:
                        new_attributes[attr] = self._changes[attr][0][1]
                    result = self.entry_cursor.connection.add(self.entry_dn, None, new_attributes, controls)
                else:
                    result = self.entry_cursor.connection.modify(self.entry_dn, self._changes, controls)

                if not self.entry_cursor.connection.strategy.sync:  # async request
                    response, result, request = self.entry_cursor.connection.get_response(result, get_request=True)
                else:
                    response = self.entry_cursor.connection.response
                    result = self.entry_cursor.connection.result
                    request = self.entry_cursor.connection.request
                self.entry_cursor._store_operation_in_history(request, result, response)

                if result['result'] == RESULT_SUCCESS:
                    if refresh:
                        if self.entry_refresh():
                            if self._state.origin and self.entry_cursor.connection.server == self._state.origin.entry_cursor.connection.server:  # updates original read-only entry if present
                                for attr in self:  # adds AttrDefs from writable entry to origin entry definition if some is missing
                                    if attr.key in self.entry_definition._attributes and attr.key not in self._state.origin.entry_definition._attributes:
                                        self._state.origin.entry_cursor.definition.add_attribute(self.entry_cursor.definition._attributes[attr.key])  # adds AttrDef from writable entry to original entry if missing
                                temp_entry = self._state.origin.entry_cursor._create_entry(self._state.response)
                                self._state.origin.__dict__.clear()
                                self._state.origin.__dict__['_state'] = temp_entry._state
                                for attr in self:  # returns the whole attribute object
                                    if not attr.virtual:
                                        self._state.origin.__dict__[attr.key] = self._state.origin._state.attributes[attr.key]
                                self._state.origin._state.read_time = self.entry_read_time
                    else:
                        self.entry_discard_changes()  # if not refreshed remove committed changes
                    self._state.set_status(STATUS_COMMITTED)
                    return True
                # raise LDAPCursorError('unable to commit changes to entry %s, reason: %s - %s' % (self.entry_dn, result['description'], result['message']))
        return False

    def entry_discard_changes(self):
        self._changes.clear()
        self._state.set_status(self._state._initial_status)

    def entry_delete(self):
        if self.entry_status not in [STATUS_WRITABLE, STATUS_COMMITTED, STATUS_READY_FOR_DELETION]:
            raise LDAPCursorError('unable to delete entry, invalid status: ' + self.entry_status)
        self._state.set_status(STATUS_READY_FOR_DELETION)

    def entry_refresh(self, tries=4, seconds=2):
        """

        Refreshes the entry from the LDAP Server
        """
        if self.entry_cursor.connection:
            if self.entry_cursor.refresh_entry(self, tries, seconds):
                return True

        return False

    def entry_move(self, destination_dn):
        if self.entry_status not in [STATUS_WRITABLE, STATUS_COMMITTED, STATUS_READY_FOR_MOVING]:
            raise LDAPCursorError('unable to move entry, invalid status: ' + self.entry_status)
        self._state._to = safe_dn(destination_dn)
        self._state.set_status(STATUS_READY_FOR_MOVING)

    def entry_rename(self, new_name):
        if self.entry_status not in [STATUS_WRITABLE, STATUS_COMMITTED, STATUS_READY_FOR_RENAMING]:
            raise LDAPCursorError('unable to rename entry, invalid status: ' + self.entry_status)
        self._state._to = new_name
        self._state.set_status(STATUS_READY_FOR_RENAMING)

    @property
    def entry_changes(self):
        return self._changes
