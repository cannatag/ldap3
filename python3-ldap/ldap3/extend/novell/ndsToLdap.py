"""
Created on 2014.04.30

@author: Giovanni Cannata

Copyright 2014 Giovanni Cannata

This file is part of python3-ldap.

python3-ldap is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

python3-ldap is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with python3-ldap in the COPYING and COPYING.LESSER files.
If not, see <http://www.gnu.org/licenses/>.
"""
from pyasn1.type.univ import OctetString
from ...protocol.novell import NdsToLdapRequestValue, NdsToLdapResponseValue, Identity, NMAS_LDAP_EXT_VERSION
from ..operation import ExtendedOperation


class NdsToLdap(ExtendedOperation):
    def config(self):
        self.request_name = '2.16.840.1.113719.1.39.42.100.1'
        self.response_name = '2.16.840.1.113719.1.39.42.100.2'
        self.request_value = NdsToLdapRequestValue()
        self.asn1_spec = NdsToLdapResponseValue()
        self.response_attribute = 'user'

    def __init__(self, connection, user):
        ExtendedOperation.__init__(self, connection)  # calls super __init__()
        self.request_value['nmasver'] = NMAS_LDAP_EXT_VERSION
        self.request_value['reqdn'] = user

    def populate_result(self):
        try:
            self.result['user'] = str(self.decoded_response['user']) if self.decoded_response['user'] else None
        except TypeError:
            self.result['user'] = None