"""
"""

# Created on 2013.05.31
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

from pyasn1.type.univ import OctetString
from pyasn1.codec.ber import encoder
from pyasn1.type.base import Asn1Item

from ..protocol.rfc4511 import ExtendedRequest, RequestName, ResultCode, RequestValue
from ldap3.protocol.convert import decode_referrals



# ExtendedRequest ::= [APPLICATION 23] SEQUENCE {
#     requestName      [0] LDAPOID,
#     requestValue     [1] OCTET STRING OPTIONAL }


def extended_operation(request_name,
                       request_value=None):
    request = ExtendedRequest()
    request['requestName'] = RequestName(request_name)
    if request_value and isinstance(request_value, Asn1Item):
        request['requestValue'] = RequestValue(encoder.encode(request_value))
    elif str != bytes and isinstance(request_value, (bytes, bytearray)):  # in python3 doesn't try to encode a byte value
        request['requestValue'] = request_value
    elif request_value:  # tries to encode as a octet string
        request['requestValue'] = RequestValue(encoder.encode(OctetString(str(request_value))))
    #elif request_value is not None:
    #    raise LDAPExtensionError('unable to encode value for extended operation')
    return request


def extended_request_to_dict(request):
    return {'name': str(request['requestName']), 'value': str(request['requestValue']) if request['requestValue'] else None}


def extended_response_to_dict(response):
    return {'result': int(response[0]),
            'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']),
            'description': ResultCode().getNamedValues().getName(response[0]),
            'referrals': decode_referrals(response['referral']),
            'responseName': str(response['responseName']) if response['responseName'] else None,
            'responseValue': bytes(response['responseValue']) if response['responseValue'] else bytes()}


def intermediate_response_to_dict(response):
    return {'responseName': str(response['responseName']),
            'responseValue': bytes(response['responseValue']) if response['responseValue'] else bytes()}
