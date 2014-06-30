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

# implements rfc4532

from ..protocol.rfc4532 import AuthzId
from pyasn1.codec.ber import decoder


def who_am_i(connection):
    resp = connection.extended('1.3.6.1.4.1.4203.1.11.3', None)
    if not connection.strategy.sync:
        _, result = connection.get_response(resp)
    else:
        result = connection.result

    connection.response = decode_response(result)
    populate_result_dict(result, connection.response)
    return connection.response


def populate_result_dict(result, value):
    result['AuthzId'] = value


def decode_response(result):
    if result['responseValue']:
        decoded = result['responseValue'].decode('utf-8')
        return decoded

    return None