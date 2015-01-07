"""
"""

# Created on 2014.07.04
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

from pyasn1.codec.ber import decoder

from .. import RESULT_SUCCESS
from ..core.exceptions import LDAPExtensionError


class ExtendedOperation(object):
    def __init__(self, connection):
        self.connection = connection
        self.decoded_response = None
        self.result = None
        self.asn1_spec = None  # if None the response_value is returned without encoding
        self.request_name = None
        self.response_name = None
        self.request_value = None
        self.response_value = None
        self.response_attribute = None
        self.config()

    def send(self):
        if self.connection.check_names and self.connection.server.info is not None and self.connection.server.info.supported_extensions is not None:  # checks if extension is supported
            for request_name in self.connection.server.info.supported_extensions:
                if request_name.oid == self.request_name:
                    break
            else:
                raise LDAPExtensionError('extension not in DSA list of supported extensions')

        resp = self.connection.extended(self.request_name, self.request_value)
        if not self.connection.strategy.sync:
            _, self.result = self.connection.get_response(resp)
        else:
            self.result = self.connection.result
        self.decode_response()
        self.populate_result()
        self.set_response()
        return self.response_value

    def populate_result(self):
        pass

    def decode_response(self):
        if not self.result:
            return None
        if self.result['result'] not in [RESULT_SUCCESS]:
            raise LDAPExtensionError('extended operation error: ' + self.result['description'] + ' - ' + self.result['message'])
        if not self.response_name or self.result['responseName'] == self.response_name:
            if self.result['responseValue']:
                if self.asn1_spec is not None:
                    decoded, unprocessed = decoder.decode(self.result['responseValue'], asn1Spec=self.asn1_spec)
                    if unprocessed:
                        raise LDAPExtensionError('error decoding extended response value')
                    self.decoded_response = decoded
                else:
                    self.decoded_response = self.result['responseValue']
        else:
            raise LDAPExtensionError('invalid response name received')

    def set_response(self):
        self.response_value = self.result[self.response_attribute] if self.result and self.response_attribute in self.result else None
        self.connection.response = self.response_value

    def config(self):
        pass
