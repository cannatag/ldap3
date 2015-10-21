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
                 cookie=None,
                 parent_first=True,
                 max_length=65535,
                 hex_guid=False
                 ):
        self.connection = connection
        self.base = sync_base
        self.filter = sync_filter
        self.attributes = attributes if attributes in SEQUENCE_TYPES else ()
        self.cookie = cookie
        self.parent_first = parent_first
        self.max_length = max_length
        self.hex_guid = hex_guid
        self.active = False

    def stop(self):
        self.active = False
        self.loop()

    def start(self):
        self.active = True
        self.loop()

    def loop(self):
        while self.active:
            result = self.connection.search(self.base,
                                            self.filter,
                                            SUBTREE,
                                            self.attributes,
                                            controls=[dir_sync_control(criticality=True, parent_first=self.parent_first, max_length=self.max_length, cookie=self.cookie),
                                                      extended_dn_control(criticality=True, hex_format=self.hex_guid),
                                                      show_deleted_control(criticality=True)]
                                            )
            if not self.connection.strategy.sync:
                response, result = self.connection.get_response(result)
            else:
                response = self.connection.response
                result = self.connection.result

            if result['description'] == 'success':
                yield response
            else:
                raise LDAPExtensionError('error %s in DirSync' % result['description'])
