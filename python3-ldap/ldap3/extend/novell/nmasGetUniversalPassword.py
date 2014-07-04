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
from ...core.exceptions import LDAPExtensionError
from ldap3 import RESULT_SUCCESS
from ...protocol.novell import NmasGetUniversalPasswordRequestValue, NmasGetUniversalPasswordResponseValue, NMAS_LDAP_EXT_VERSION
from pyasn1.codec.ber import decoder

REQUEST_NAME = '2.16.840.1.113719.1.39.42.100.13'
RESPONSE_NAME = '2.16.840.1.113719.1.39.42.100.14'


def nmas_get_universal_password(connection, user_dn):
    request_value = NmasGetUniversalPasswordRequestValue()
    request_value['nmasver'] = NMAS_LDAP_EXT_VERSION
    request_value['reqdn'] = user_dn
    resp = connection.extended(REQUEST_NAME, request_value)
    if not connection.strategy.sync:
        _, result = connection.get_response(resp)
    else:
        result = connection.result

    decoded_response = decode_response(result)
    populate_result_dict(result, decoded_response)
    connection.response = connection.result['password'] if 'password' in connection.result else ''
    return connection.response


def populate_result_dict(result, value):
    result['nmasver'] = int(value['nmasver'])
    result['error'] = int(value['err'])
    result['password'] = str(value['passwd'])


def decode_response(result):
    if result['result'] not in [RESULT_SUCCESS]:
        raise LDAPExtensionError('extended operation error: ' + result['description'])
    if not RESPONSE_NAME or result['responseName'] == RESPONSE_NAME:
        if result['responseValue']:
            decoded, unprocessed = decoder.decode(result['responseValue'], asn1Spec=NmasGetUniversalPasswordResponseValue())
            if unprocessed:
                raise LDAPExtensionError('error decoding extended response value')
            return decoded
        else:
            return None
    else:
        raise LDAPExtensionError('invalid response name received')