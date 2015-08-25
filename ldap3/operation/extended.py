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
from pyasn1.type.base import Asn1Item

from .. import RESULT_CODES
from ..protocol.rfc4511 import ExtendedRequest, RequestName, ResultCode, RequestValue
from ..protocol.convert import decode_referrals, referrals_to_list
from ..utils.asn1 import encoder

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
    # elif request_value is not None:
    #     raise LDAPExtensionError('unable to encode value for extended operation')
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


def extended_response_to_dict_fast(response):
    response_dict = dict()
    response_dict['result'] = int(response[0][3])  # resultCode
    response_dict['description'] = RESULT_CODES[response_dict['result']]
    response_dict['dn'] = response[1][3].decode('utf-8')  # matchedDN
    response_dict['message'] = response[2][3].decode('utf-8')  # diagnosticMessage
    response_dict['referrals'] = None  # referrals
    response_dict['responseName'] = None  # referrals
    response_dict['responseValue'] = None  # responseValue

    for r in response[3:]:
        if r[2] == 3:  # referrals
            response_dict['referrals'] = referrals_to_list(r[3])  # referrals
        elif r[2] == 10:  # responseName
            response_dict['responseName'] = r[3].decode('utf-8')
            response_dict['responseValue'] = b''  # responseValue could be empty

        else:  # responseValue (11)
            response_dict['responseValue'] = bytes(r[3])

    return response_dict


def intermediate_response_to_dict_fast(response):
    response_dict = dict()
    for r in response:
        if r[2] == 0:  # responseName
            response_dict['responseName'] = r[3].decode('utf-8')
        else:  # responseValue (1)
            response_dict['responseValue'] = bytes(r[3])

    return response_dict
