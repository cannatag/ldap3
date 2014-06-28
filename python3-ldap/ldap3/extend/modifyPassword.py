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
from ..protocol.rfc3062 import PasswdModifyRequestValue, PasswdModifyResponseValue
from pyasn1.codec.ber import encoder, decoder


def modify_password(connection, user, old_password, new_password):
    request = PasswdModifyRequestValue()
    request['userIdentity'] = user
    request['oldPasswd'] = old_password
    request['newPasswd'] = new_password

    resp = connection.extended('1.3.6.1.4.1.4203.1.11.1', request)
    if not connection.strategy.sync:
        response, result = connection.get_response(resp)
    else:
        response = connection.response
        result = connection.result

    return modify_password_decode_response_value(response), result


def modify_password_request_to_dict(request):
    return {'userIdentity': str(request['userIdentity']),
            'oldPasswd': str(request['oldPasswd']),
            'newPasswd': str(request['newPasswd'])}


def modify_password_response_value_to_dict(value):
    return {'genPasswd': str(value['genPasswd'])}


def modify_password_decode_response_value(response):
    if response['value']:
        decoded, unprocessed = decoder.decode(response['value'], asn1Spec=PasswdModifyResponseValue())
        if unprocessed:
            raise LDAPException('error decoding extended response value')

        response['value'] = modify_password_response_value_to_dict(decoded)
