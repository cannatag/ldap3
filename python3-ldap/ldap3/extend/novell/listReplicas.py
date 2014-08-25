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
from ...protocol.novell import ReplicaList
from ...protocol.rfc4511 import LDAPDN


class ListReplicas(ExtendedOperation):
    def config(self):
        self.request_name = '2.16.840.1.113719.1.27.100.19'
        self.response_name = '2.16.840.1.113719.1.27.100.20'
        self.request_value = LDAPDN()
        self.asn1_spec = ReplicaList()
        self.response_attribute = 'replicas'

    def __init__(self, connection, server_dn):
        ExtendedOperation.__init__(self, connection)  # calls super __init__()
        self.request_value = LDAPDN(server_dn)

    def populate_result(self):
        try:
            self.result['replicas'] = str(self.decoded_response['replicaList']) if self.decoded_response['replicaList'] else None
        except TypeError:
            self.result['replicas'] = None