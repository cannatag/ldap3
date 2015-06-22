"""
"""

# Created on 2014.01.06
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

from datetime import datetime
from os import linesep

from .. import SUBTREE, LEVEL, DEREF_ALWAYS, BASE, ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX, STRING_TYPES, SEQUENCE_TYPES
from .attribute import Attribute
from .entry import Entry
from ..core.exceptions import LDAPReaderError
from .operationalAttribute import OperationalAttribute


def _ret_search_value(value):
    return value[0] + '=' + value[1:] if value[0] in '<>~' and value[1] != '=' else value


def _create_query_dict(query_text):
    """
    Create a dictionary with query key:value definitions
    query_text is a comma delimited key:value sequence
    """
    query_dict = dict()
    if query_text:
        for arg_value_str in query_text.split(','):
            if ':' in arg_value_str:
                arg_value_list = arg_value_str.split(':')
                query_dict[arg_value_list[0].strip()] = arg_value_list[1].strip()

    return query_dict


class Reader(object):
    """Reader object to perform searches:

    :param connection: the LDAP connection object to use
    :type connection: LDAPConnection
    :param object_def: the ObjectDef of the LDAP object returned
    :type object_def: ObjectDef
    :param query: the simplified query (will be transformed in an LDAP filter)
    :type query: str
    :param base: starting base of the search
    :type base: str
    :param components_in_and: specify if assertions in the query mus be all satisfied or not (AND/OR)
    :type components_in_and: bool
    :param sub_tree: specify if the search must be performed ad Single Level (False) or Whole SubTree (True)
    :type sub_tree: bool
    :param get_operational_attributes: specify if operational attributes are returned or not
    :type get_operational_attributes: bool
    :param controls: controls to be used in search
    :type controls: tuple

    """
    def __init__(self, connection, object_def, query, base, components_in_and=True, sub_tree=True, get_operational_attributes=False, controls=None):
        self.connection = connection
        self._definition = object_def
        self.base = base
        self._components_in_and = components_in_and
        self.attributes = sorted([attr.name for attr in self._definition])
        self.get_operational_attributes = get_operational_attributes
        self.controls = controls
        self.sub_tree = sub_tree
        self._query = query
        self.dereference_aliases = DEREF_ALWAYS
        self.size_limit = 0
        self.time_limit = 0
        self.types_only = False
        self.validated_query = None
        self._query_dict = dict()
        self._validated_query_dict = dict()
        self.execution_time = None
        self.query_filter = None
        self.entries = []
        self.last_sub_tree = None
        self.reset()

    @property
    def definition(self):
        return self._definition

    @property
    def query(self):
        return self._query

    @query.setter
    def query(self, value):
        self._query = value
        self.reset()

    @property
    def components_in_and(self):
        return self._components_in_and

    @components_in_and.setter
    def components_in_and(self, value):
        self._components_in_and = value
        self.reset()

    def __repr__(self):
        r = 'CONN   : ' + str(self.connection) + linesep
        r += 'BASE   : ' + repr(self.base) + (' [SUB]' if self.sub_tree else ' [LEVEL]') + linesep
        r += 'DEFS   : ' + repr(self._definition.object_class) + ' ['
        for attr_def in sorted(self._definition):
            r += (attr_def.key if attr_def.key == attr_def.name else (attr_def.key + ' <' + attr_def.name + '>')) + ', '
        if r[-2] == ',':
            r = r[:-2]
        r += ']' + linesep
        r += 'QUERY  : ' + repr(self._query) + (' [AND]' if self.components_in_and else ' [OR]') + linesep
        r += 'PARSED : ' + repr(self.validated_query) + (' [AND]' if self.components_in_and else ' [OR]') + linesep
        r += 'ATTRS  : ' + repr(self.attributes) + (' [OPERATIONAL]' if self.get_operational_attributes else '') + linesep
        r += 'FILTER : ' + repr(self.query_filter) + linesep
        if self.execution_time:
            r += 'ENTRIES: ' + str(len(self.entries))
            r += ' [SUB]' if self.last_sub_tree else ' [level]'
            r += ' [SIZE LIMIT: ' + str(self.size_limit) + ']' if self.size_limit else ''
            r += ' [TIME LIMIT: ' + str(self.time_limit) + ']' if self.time_limit else ''
            r += ' [executed at: ' + str(self.execution_time.isoformat()) + ']' + linesep
        return r

    def __str__(self):
        return self.__repr__()

    def clear(self):
        """Clear the Reader search parameters

        """
        self.dereference_aliases = DEREF_ALWAYS
        self.size_limit = 0
        self.time_limit = 0
        self.types_only = False

    def reset(self):
        """Clear all the Reader parameters
        """
        self.clear()
        self.validated_query = None
        self._query_dict = dict()
        self._validated_query_dict = dict()
        self.execution_time = None
        self.query_filter = None
        self.entries = []
        self.last_sub_tree = None
        self._create_query_filter()

    def __iter__(self):
        return self.entries.__iter__()

    def __getitem__(self, item):
        return self.entries[item]

    def __len__(self):
        return len(self.entries)

    def _validate_query(self):
        """Processes the text query and verifies that the requested friendly names are in the Reader dictionary
        If the AttrDef has a 'validate' property the callable is executed and if it returns False an Exception is raised

        """
        if not self._query_dict:
            self._query_dict = _create_query_dict(self._query)

        query = ''
        for d in sorted(self._query_dict):
            attr = d[1:] if d[0] in '&|' else d
            for attr_def in self._definition:
                if ''.join(attr.split()).lower() == attr_def.key.lower():
                    attr = attr_def.key
                    break

            if attr in self._definition:
                vals = sorted(self._query_dict[d].split(';'))

                query += (d[0] + attr if d[0] in '&|' else attr) + ': '
                for val in vals:
                    val = val.strip()
                    val_not = True if val[0] == '!' else False
                    val_search_operator = '='  # default
                    if val_not:
                        if val[1:].lstrip()[0] not in '=<>~':
                            value = val[1:].lstrip()
                        else:
                            val_search_operator = val[1:].lstrip()[0]
                            value = val[1:].lstrip()[1:]
                    else:
                        if val[0] not in '=<>~':
                            value = val.lstrip()
                        else:
                            val_search_operator = val[0]
                            value = val[1:].lstrip()

                    if self._definition[attr].validate:
                        if not self._definition[attr].validate(self._definition[attr].key, value):
                            raise LDAPReaderError('validation failed for attribute %s and value %s' % (d, val))

                    if val_not:
                        query += '!' + val_search_operator + value
                    else:
                        query += val_search_operator + value

                    query += ';'
                query = query[:-1] + ', '

        self.validated_query = query[:-2]
        self._validated_query_dict = _create_query_dict(self.validated_query)

    def _create_query_filter(self):
        """Converts the query dictionary in the filter text"""
        if self._query and self._query.startswith('(') and self._query.endswith(')'):  # query is already an LDAP filter
            self.query_filter = self._query
            return

        self.query_filter = ''

        if self._definition.object_class:
            self.query_filter += '(&'
            if isinstance(self._definition.object_class, STRING_TYPES):
                self.query_filter += '(objectClass=' + self._definition.object_class + ')'
            elif isinstance(self._definition.object_class, SEQUENCE_TYPES):
                self.query_filter += '(&'
                for object_class in self._definition.object_class:
                    self.query_filter += '(objectClass=' + object_class + ')'
                self.query_filter += ')'
            else:
                raise LDAPReaderError('object_class must be a string or a list')

        if not self.components_in_and:
            self.query_filter += '(|'
        elif not self._definition.object_class:
            self.query_filter += '(&'

        self._validate_query()

        attr_counter = 0
        for attr in sorted(self._validated_query_dict):
            attr_counter += 1
            multi = True if ';' in self._validated_query_dict[attr] else False
            vals = sorted(self._validated_query_dict[attr].split(';'))
            attr_def = self._definition[attr[1:]] if attr[0] in '&|' else self._definition[attr]
            if attr_def.pre_query:
                modvals = []
                for val in vals:
                    modvals.append(val[0] + attr_def.pre_query(attr_def.key, val[1:]))
                vals = modvals
            if multi:
                if attr[0] in '&|':
                    self.query_filter += '(' + attr[0]
                else:
                    self.query_filter += '(|'

            for val in vals:
                if val[0] == '!':
                    self.query_filter += '(!(' + attr_def.name + _ret_search_value(val[1:]) + '))'
                else:
                    self.query_filter += '(' + attr_def.name + _ret_search_value(val) + ')'
            if multi:
                self.query_filter += ')'

        if not self.components_in_and:
            self.query_filter += '))'
        else:
            self.query_filter += ')'

        if not self._definition.object_class and attr_counter == 1:  # remove unneeded starting filter
            self.query_filter = self.query_filter[2: -1]

    def _get_attributes(self, response, attr_defs, entry):
        """Assign the result of the LDAP query to the Entry object dictionary.

        If the optional 'post_query' callable is present in the AttrDef it is called with each value of the attribute and the callable result is stored in the attribute.

        Returns the default value for missing attributes.
        If the 'dereference_dn' in AttrDef is a ObjectDef then the attribute values are treated as distinguished name and the relevant entry is retrieved and stored in the attribute value.

        """
        attributes = dict()
        used_attribute_names = []
        for attr_def in attr_defs:
            name = None
            for attr_name in response['attributes']:
                if attr_def.name.lower() == attr_name.lower():
                    name = attr_name
                    break

            if name or attr_def.default is not NotImplemented:  # attribute value found in result or default value present - NotImplemented allows use of None as default
                attribute = Attribute(attr_def, entry)
                attribute.__dict__['_response'] = response
                attribute.__dict__['raw_values'] = response['raw_attributes'][name] if name else None
                if attr_def.post_query and attr_def.name in response['attributes']:
                    attribute.__dict__['values'] = attr_def.post_query(attr_def.key, response['attributes'][name])
                else:
                    attribute.__dict__['values'] = response['attributes'][name] if name else (attr_def.default if isinstance(attr_def.default, SEQUENCE_TYPES) else [attr_def.default])
                if not isinstance(attribute.__dict__['values'], list):  # force attribute values to list (if attribute is single-valued)
                    attribute.__dict__['values'] = [attribute.__dict__['values']]
                if attr_def.dereference_dn:  # try to get object referenced in value
                    # noinspection PyUnresolvedReferences
                    if attribute.values:
                        temp_reader = Reader(self.connection, attr_def.dereference_dn, query='', base='', get_operational_attributes=self.get_operational_attributes, controls=self.controls)
                        temp_values = []

                        # noinspection PyUnresolvedReferences
                        for element in attribute.values:
                            temp_values.append(temp_reader.search_object(element))
                        del temp_reader  # remove the temporary Reader
                        attribute.__dict__['values'] = temp_values

                # noinspection PyUnresolvedReferences
                attributes[attribute.key] = attribute
                used_attribute_names.append(name)

        for name in response['attributes']:
            if name not in used_attribute_names:
                attribute = OperationalAttribute(ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX + name, entry)
                attribute.__dict__['raw_values'] = response['raw_attributes'][name]
                attribute.__dict__['values'] = response['attributes'][name]
                if (ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX + name) not in attributes:
                    attributes[ABSTRACTION_OPERATIONAL_ATTRIBUTE_PREFIX + name] = attribute

        return attributes

    def _get_entry(self, response):
        if not response['type'] == 'searchResEntry':
            return None

        entry = Entry(response['dn'], self)
        entry.__dict__['_attributes'] = self._get_attributes(response, self._definition, entry)
        entry.__dict__['_raw_attributes'] = response['raw_attributes']
        for attr in entry:  # returns the whole attribute object
            attr_name = attr.key
            entry.__dict__[attr_name] = attr

        return entry

    def _execute_query(self, query_scope):
        if not self.connection:
            raise LDAPReaderError('no connection established')

        self._create_query_filter()
        with self.connection:
            result = self.connection.search(search_base=self.base,
                                            search_filter=self.query_filter,
                                            search_scope=query_scope,
                                            dereference_aliases=self.dereference_aliases,
                                            attributes=self.attributes,
                                            size_limit=self.size_limit,
                                            time_limit=self.time_limit,
                                            types_only=self.types_only,
                                            get_operational_attributes=self.get_operational_attributes,
                                            controls=self.controls)
            if not self.connection.strategy.sync:
                response, _ = self.connection.get_response(result)
            else:
                response = self.connection.response

            self.entries = []
            for r in response:
                entry = self._get_entry(r)
                self.entries.append(entry)

            self.last_sub_tree = self.sub_tree
            self.execution_time = datetime.now()

    def search(self):
        """Perform the LDAP search

        :return: Entries found in search

        """
        self.clear()
        query_scope = SUBTREE if self.sub_tree else LEVEL
        self._execute_query(query_scope)

        return self.entries

    def search_level(self):
        """Perform the LDAP search operation with SINGLE_LEVEL scope

        :return: Entries found in search

        """
        self.clear()
        self._execute_query(LEVEL)

        return self.entries

    def search_subtree(self):
        """Perform the LDAP search operation WHOLE_SUBTREE scope

        :return: Entries found in search

        """
        self.clear()
        self._execute_query(SUBTREE)

        return self.entries

    def search_object(self, entry_dn=None):  # base must be a single dn
        """Perform the LDAP search operation SINGLE_OBJECT scope

        :return: Entry found in search

        """
        self.clear()
        if entry_dn:
            old_base = self.base
            self.base = entry_dn
            self._execute_query(BASE)
            self.base = old_base
        else:
            self._execute_query(BASE)

        return self.entries[0] if len(self.entries) > 0 else None

    def search_size_limit(self, size_limit):
        """Perform the LDAP search with limit of entries found

        :param size_limit: maximum number of entries returned
        :return: Entries found in search

        """

        self.clear()
        self.size_limit = size_limit
        query_scope = SUBTREE if self.sub_tree else LEVEL
        self._execute_query(query_scope)

        return self.entries

    def search_time_limit(self, time_limit):
        """Perform the LDAP search with limit of time spent in searching by the server

        :param time_limit: maximum number of seconds to wait for a search
        :return: Entries found in search

        """
        self.clear()
        self.time_limit = time_limit
        query_scope = SUBTREE if self.sub_tree else LEVEL
        self._execute_query(query_scope)

        return self.entries

    def search_types_only(self):
        """Perform the search returning attribute names only.

        :return: Entries found in search

        """
        self.clear()
        self.types_only = True
        query_scope = SUBTREE if self.sub_tree else LEVEL
        self._execute_query(query_scope)

        return self.entries

    def search_paged(self, paged_size, paged_criticality=True, generator=True):
        """Perform a paged search, can be called as an Iterator

        :param paged_size: number of entries returned in each search
        :type paged_size: int
        :param paged_criticality: specify if server must not execute the search if it is not capable of paging searches
        :type paged_criticality: bool
        :param generator: if True the paged searches are executed while generating the entries,
                          if False all the paged searches are execute before returning the generator
        :type generator: bool
        :return: Entries found in search

        """
        if not self.connection:
            raise LDAPReaderError('no connection established')

        self.clear()
        self._create_query_filter()
        self.entries = []
        self.last_sub_tree = self.sub_tree
        self.execution_time = datetime.now()
        for response in self.connection.extend.standard.paged_search(search_base=self.base,
                                                                     search_filter=self.query_filter,
                                                                     search_scope=SUBTREE if self.sub_tree else LEVEL,
                                                                     dereference_aliases=self.dereference_aliases,
                                                                     attributes=self.attributes,
                                                                     size_limit=self.size_limit,
                                                                     time_limit=self.time_limit,
                                                                     types_only=self.types_only,
                                                                     get_operational_attributes=self.get_operational_attributes,
                                                                     controls=self.controls,
                                                                     paged_size=paged_size,
                                                                     paged_criticality=paged_criticality,
                                                                     generator=generator):
            yield self._get_entry(response)
