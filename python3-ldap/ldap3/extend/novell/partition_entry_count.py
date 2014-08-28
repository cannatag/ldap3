"""
"""

# Created on 2014.08.05
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

from pyasn1.codec.ber import decoder
from pyasn1.type.univ import Integer
from ...core.exceptions import LDAPExtensionError
from ..operation import ExtendedOperation
from ...protocol.rfc4511 import LDAPDN


class PartitionEntryCount(ExtendedOperation):
    def config(self):
        self.request_name = '2.16.840.1.113719.1.27.100.13'
        self.response_name = '2.16.840.1.113719.1.27.100.14'
        self.request_value = LDAPDN()
        self.response_attribute = 'entry_count'

    def __init__(self, connection, partition_dn):
        ExtendedOperation.__init__(self, connection)  # calls super __init__()
        self.request_value = LDAPDN(partition_dn)

    def populate_result(self):
        substrate = self.decoded_response
        try:
            decoded, substrate = decoder.decode(substrate, asn1Spec=Integer())
            self.result['entry_count'] = int(decoded)
        except Exception:
            raise LDAPExtensionError('unable to decode substrate')

        if substrate:
            raise LDAPExtensionError('unknown substrate remaining')