"""
Created on 2014.07.03

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
from ..operation import ExtendedOperation
from ...protocol.novell import NmasGetUniversalPasswordRequestValue, NmasGetUniversalPasswordResponseValue, NMAS_LDAP_EXT_VERSION


class NmasGetUniversalPassword(ExtendedOperation):
    def config(self):
        self.request_name = '2.16.840.1.113719.1.39.42.100.13'
        self.response_name = '2.16.840.1.113719.1.39.42.100.14'
        self.request_value = NmasGetUniversalPasswordRequestValue()
        self.asn1_spec = NmasGetUniversalPasswordResponseValue()
        self.response_attribute = 'password'

    def __init__(self, connection, user):
        ExtendedOperation.__init__(self, connection)  # calls super __init__()
        self.request_value['nmasver'] = NMAS_LDAP_EXT_VERSION
        self.request_value['reqdn'] = user

    def populate_result(self):
        self.result['nmasver'] = int(self.decoded_response['nmasver'])
        self.result['error'] = int(self.decoded_response['err'])
        self.result['password'] = str(self.decoded_response['passwd'])