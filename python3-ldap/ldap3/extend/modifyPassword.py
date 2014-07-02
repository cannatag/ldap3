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
from ..core.exceptions import LDAPExtensionError
from ..protocol.rfc3062 import PasswdModifyRequestValue, PasswdModifyResponseValue
from pyasn1.codec.ber import decoder


def modify_password(connection, user=None, old_password=None, new_password=None):
    request = PasswdModifyRequestValue()
    if user:
        request['userIdentity'] = user
    if old_password:
        request['oldPasswd'] = old_password
    if new_password:
        request['newPasswd'] = new_password
    resp = connection.extended('1.3.6.1.4.1.4203.1.11.1', request)
    if not connection.strategy.sync:
        _, result = connection.get_response(resp)
    else:
        result = connection.result

    connection.response = decode_response(result)
    populate_result_dict(result, connection.response)

    return connection.response


def populate_result_dict(result, value):
    result['genPasswd'] = value


def modify_password_request_to_dict(request):
    return {'userIdentity': str(request['userIdentity']),
            'oldPasswd': str(request['oldPasswd']),
            'newPasswd': str(request['newPasswd'])}


def decode_response(result):
    if result['responseValue']:
        decoded, unprocessed = decoder.decode(result['responseValue'], asn1Spec=PasswdModifyResponseValue())
        if unprocessed:
            raise LDAPExtensionError('error decoding extended response value')
        return str(decoded['genPasswd'])

    return None
