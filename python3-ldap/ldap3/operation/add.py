"""
"""

# Created on 2013.05.31
#
# Author: Giovanni Cannata
#
# Copyright 2013 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from .. import SEQUENCE_TYPES
from ..protocol.rfc4511 import AddRequest, LDAPDN, AttributeList, Attribute, AttributeDescription, ValsAtLeast1, ResultCode
from ..protocol.convert import referrals_to_list, attributes_to_dict, validate_attribute_value

# AddRequest ::= [APPLICATION 8] SEQUENCE {
#     entry           LDAPDN,
#     attributes      AttributeList }


def add_operation(dn,
                  attributes,
                  schema=None):
    # attributes is a dictionary in the form 'attribute': ['val1', 'val2', 'valN']
    attribute_list = AttributeList()
    for pos, attribute in enumerate(attributes):
        attribute_list[pos] = Attribute()
        attribute_list[pos]['type'] = AttributeDescription(attribute)
        vals = ValsAtLeast1()
        if isinstance(attributes[attribute], SEQUENCE_TYPES):
            for index, value in enumerate(attributes[attribute]):
                vals.setComponentByPosition(index, validate_attribute_value(schema, attribute, value))
        else:
            vals.setComponentByPosition(0, validate_attribute_value(schema, attribute, attributes[attribute]))

        attribute_list[pos]['vals'] = vals

    request = AddRequest()
    request['entry'] = LDAPDN(dn)
    request['attributes'] = attribute_list

    return request


def add_request_to_dict(request):
    return {'entry': str(request['entry']),
            'attributes': attributes_to_dict(request['attributes'])}


def add_response_to_dict(response):
    return {'result': int(response[0]),
            'description': ResultCode().getNamedValues().getName(response[0]),
            'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']),
            'referrals': referrals_to_list(response['referral'])}

