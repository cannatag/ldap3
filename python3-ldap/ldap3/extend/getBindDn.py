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

    from ..protocol.novell import Identity


from pyasn1.codec.ber import decoder


def get_bind_dn(connection):
    resp = connection.extended('2.16.840.1.113719.1.27.100.31', None)
    if not connection.strategy.sync:
        _, result = connection.get_response(resp)
    else:
        result = connection.result

    connection.response = decode_response(result)
    populate_result_dict(result, connection.response)

    return connection.response


def populate_result_dict(result, value):
    result['identity'] = value


def decode_response(result):
    if result['responseValue']:
        decoded, unprocessed = decoder.decode(result['responseValue'], asn1Spec=Identity())
        if unprocessed:
            raise LDAPException('error decoding extended response value')
        return str(decoded)

    return str(result) if result else ''
