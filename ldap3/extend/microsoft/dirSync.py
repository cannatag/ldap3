"""
"""

# Created on 2015.10.21
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
from ldap3.core.exceptions import LDAPExtensionError
from ...protocol.microsoft import dir_sync_control, extended_dn_control, show_deleted_control
from ... import SEQUENCE_TYPES, SUBTREE


class DirSync(object):
    def __init__(self,
                 connection,
                 sync_base,
                 sync_filter='(objectclass=*)',
                 attributes=('*',),
                 cookie='',
                 object_security=False,
                 ancestors_first=True,
                 public_data_only=False,
                 incremental_values=True,
                 max_length=65535,
                 hex_guid=False
                 ):
        self.connection = connection
        self.base = sync_base
        self.filter = sync_filter
        self.attributes = attributes if attributes in SEQUENCE_TYPES else ()
        self.cookie = cookie
        self.object_security = object_security
        self.ancestors_first = ancestors_first
        self.public_data_only = public_data_only
        self.incremental_values = incremental_values
        self.max_length = max_length
        self.hex_guid = hex_guid
        self.active = True

    def stop(self):
        self.active = False
        return self.loop()

    def start(self):
        self.active = True

    def loop(self):
        while self.active:
            result = self.connection.search(search_base=self.base,
                                            search_filter=self.filter,
                                            search_scope=SUBTREE,
                                            attributes=self.attributes,
                                            controls=[dir_sync_control(criticality=True,
                                                                       object_security=self.object_security,
                                                                       ancestors_first=self.ancestors_first,
                                                                       public_data_only=self.public_data_only,
                                                                       incremental_values=self.incremental_values,
                                                                       max_length=self.max_length, cookie=self.cookie),
                                                      extended_dn_control(criticality=True, hex_format=self.hex_guid),
                                                      show_deleted_control(criticality=True)]
                                            )
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
                result = self.connection.result

            if result['description'] == 'success':
                return response
            else:
                raise LDAPExtensionError('error %s in DirSync' % result['description'])
