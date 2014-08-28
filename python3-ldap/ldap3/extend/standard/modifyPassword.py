"""
"""

# Created on 2014.04.30
#
# Author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from ..operation import ExtendedOperation
from ...protocol.rfc3062 import PasswdModifyRequestValue, PasswdModifyResponseValue

# implements RFC3062


class ModifyPassword(ExtendedOperation):
    def config(self):
        self.request_name = '1.3.6.1.4.1.4203.1.11.1'
        self.request_value = PasswdModifyRequestValue()
        self.asn1_spec = PasswdModifyResponseValue()
        self.response_attribute = 'new_password'

    def __init__(self, connection, user=None, old_password=None, new_password=None):
        ExtendedOperation.__init__(self, connection)  # calls super __init__()
        if user:
            self.request_value['userIdentity'] = user
        if old_password:
            self.request_value['oldPasswd'] = old_password
        if new_password:
            self.request_value['newPasswd'] = new_password

    def populate_result(self):
        try:
            self.result['new_password'] = str(self.decoded_response['genPasswd'])
        except TypeError:  # optional field can be absent
            self.result['new_password'] = None