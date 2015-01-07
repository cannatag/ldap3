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

from ..protocol.convert import validate_attribute_value
from ..protocol.rfc4511 import CompareRequest, AttributeValueAssertion, AttributeDescription, LDAPDN, AssertionValue, ResultCode
from ..operation.search import ava_to_dict
from ..operation.bind import referrals_to_list

# CompareRequest ::= [APPLICATION 14] SEQUENCE {
#     entry           LDAPDN,
#     ava             AttributeValueAssertion }


def compare_operation(dn,
                      attribute,
                      value,
                      schema=None):
    ava = AttributeValueAssertion()
    ava['attributeDesc'] = AttributeDescription(attribute)
    ava['assertionValue'] = AssertionValue(validate_attribute_value(schema, attribute, value))

    request = CompareRequest()
    request['entry'] = LDAPDN(dn)
    request['ava'] = ava

    return request


def compare_request_to_dict(request):
    ava = ava_to_dict(request['ava'])
    return {'entry': str(request['entry']),
            'attribute': ava['attribute'],
            'value': ava['value']}


def compare_response_to_dict(response):
    return {'result': int(response[0]),
            'description': ResultCode().getNamedValues().getName(response[0]),
            'dn': str(response['matchedDN']), 'message': str(response['diagnosticMessage']),
            'referrals': referrals_to_list(response['referral'])}
