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

from os import linesep
import json
from .. import STRING_TYPES
from ..core.exceptions import LDAPKeyError, LDAPAttributeError, LDAPEntryError
from ..utils.conv import check_json_dict, format_json, prepare_for_stream
from ..protocol.rfc2849 import operation_to_ldif, add_ldif_header
from ..utils.repr import to_stdout_encoding


class Entry(object):
    """The Entry object contains a single entry from the result of an LDAP
    search.  Attributes can be accessed either by sequence, by assignment
    or as dictionary keys. Keys are not case sensitive.

    The Entry object is read only

    - The DN is retrieved by get_entry_dn()
    - The Reader reference is in get_entry_reader()
    - Raw attributes values are retrieved by the get_raw_attributes() and
      get_raw_attribute() methods

    """

    def __init__(self, dn, reader):
        self.__dict__['_attributes'] = dict()
        self.__dict__['_dn'] = dn
        self.__dict__['_raw_attributes'] = None
        self.__dict__['_response'] = None
        self.__dict__['_reader'] = reader

    def __repr__(self):
        if self._dn:
            r = 'DN: ' + to_stdout_encoding(self._dn) + linesep
            if self._attributes:
                for attr in sorted(self._attributes):
                    r += ' ' * 4 + repr(self._attributes[attr]) + linesep
            return r
        else:
            return object.__repr__(self)

    def __str__(self):
        return self.__repr__()

    def __iter__(self):
        for attribute in self._attributes:
            yield self._attributes[attribute]
        raise StopIteration

    def __contains__(self, item):
        return True if self.__getitem__(item) else False

    def __getattr__(self, item):
        if isinstance(item, STRING_TYPES):
            item = ''.join(item.split()).lower()
            for attr in self._attributes:
                if item == attr.lower():
                    break
            else:
                raise LDAPKeyError('key not found')
            return self._attributes[attr]

        raise LDAPKeyError('key must be a string')

    def __setattr__(self, item, value):
        if item in self._attributes:
            raise LDAPAttributeError('attribute is read only')
        else:
            raise LDAPEntryError('entry is read only')

    def __getitem__(self, item):
        return self.__getattr__(item)

    def __eq__(self, other):
        if isinstance(other, Entry):
            return self._dn == other.entry_get_dn()

        return False

    def __lt__(self, other):
        if isinstance(other, Entry):
            return self._dn <= other.entry_get_dn()

        return False

    def entry_get_dn(self):
        """

        :return: The distinguished name of the Entry
        """
        return self._dn

    def entry_get_response(self):
        """

        :return: The origininal search response for the Entry
        """
        return self._dn

    def entry_get_reader(self):
        """

        :return: the Reader object of the Entry
        """
        return self._reader

    def entry_get_raw_attributes(self):
        """

        :return: The raw (unencoded) attributes of the Entry as bytes
        """
        return self._raw_attributes

    def entry_get_raw_attribute(self, name):
        """

        :param name: name of the attribute
        :return: raw (unencoded) value of the attribute, None if attribute is not found
        """
        return self._raw_attributes[name] if name in self._raw_attributes else None

    def entry_get_attribute_names(self):
        return list(self._raw_attributes.keys())

    def entry_get_attributes_dict(self):
        return dict((attribute_key, attribute_value.values) for (attribute_key, attribute_value) in self._attributes.items())

    # noinspection PyProtectedMember
    def entry_refresh_from_reader(self):
        """Re-read the entry from the LDAP Server
        """
        if self.entry_get_reader():
            temp_entry = self.entry_get_reader().search_object(self.entry_get_dn())
            self.__dict__['_attributes'] = temp_entry._attributes
            self.__dict__['_raw_attributes'] = temp_entry._raw_attributes
            del temp_entry

    def entry_to_json(self,
                      raw=False,
                      indent=4,
                      sort=True,
                      stream=None):

        json_entry = dict()
        json_entry['dn'] = self.entry_get_dn()
        json_entry['attributes'] = self.entry_get_attributes_dict()
        if raw:
            json_entry['raw'] = dict(self.entry_get_raw_attributes())

        if str == bytes:
            check_json_dict(json_entry)

        json_output = json.dumps(json_entry, ensure_ascii=True, sort_keys=sort, indent=indent, check_circular=True,
                                 default=format_json, separators=(',', ': '))

        if stream:
            stream.write(json_output)

        return json_output

    def entry_to_ldif(self,
                      all_base64=False,
                      line_separator=None,
                      sort_order=None,
                      stream=None):

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
