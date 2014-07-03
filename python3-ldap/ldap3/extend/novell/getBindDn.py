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
from ...core.exceptions import LDAPExtensionError
from ...protocol.novell import Identity
from pyasn1.codec.ber import decoder

REQUEST_NAME = '2.16.840.1.113719.1.27.100.31'
RESPONSE_NAME = '2.16.840.1.113719.1.27.100.32'


def get_bind_dn(connection):
    resp = connection.extended(REQUEST_NAME, None)
    if not connection.strategy.sync:
        _, result = connection.get_response(resp)
    else:
        result = connection.result

    decoded_response = decode_response(result)
    populate_result_dict(result, decoded_response)
    connection.response = connection.result['identity'] if 'identity' in connection.result else ''
    return connection.response


def populate_result_dict(result, value):
    result['identity'] = str(value)


def decode_response(result):
    if not RESPONSE_NAME or result['responseName'] == RESPONSE_NAME:
        if result['responseValue']:
            decoded, unprocessed = decoder.decode(result['responseValue'], asn1Spec=Identity())
            if unprocessed:
                raise LDAPExtensionError('error decoding extended response value')
            return decoded
        else:
            return None
    else:
        raise LDAPExtensionError('invalid response name received')