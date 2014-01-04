"""
Created on 2013.05.31

@author: Giovanni Cannata

Copyright 2013 Giovanni Cannata

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

from ..protocol.rfc4511 import AddRequest, LDAPDN, AttributeList, Attribute, AttributeDescription, ValsAtLeast1, ResultCode
from ..protocol.convert import referralsToList, attributesToDict


# AddRequest ::= [APPLICATION 8] SEQUENCE {
#     entry           LDAPDN,
#     attributes      AttributeList }


def addOperation(dn, attributes):
    # attributes is a dictionary in the form 'attribute': ['val1', 'val2', 'valN']
    attributeList = AttributeList()
    for pos, attribute in enumerate(attributes):
        attributeList[pos] = Attribute()
        attributeList[pos]['type'] = AttributeDescription(attribute)
        vals = ValsAtLeast1()
        if isinstance(attributes[attribute], list):
            for index, value in enumerate(attributes[attribute]):
                vals.setComponentByPosition(index, value)
        else:
            vals.setComponentByPosition(0, attributes[attribute])

        attributeList[pos]['vals'] = vals

    request = AddRequest()
    request['entry'] = LDAPDN(dn)
    request['attributes'] = attributeList

    return request


def addRequestToDict(request):
    return {'entry': str(request['entry']), 'attributes': attributesToDict(request['attributes'])}


def addResponseToDict(response):
    return {'result': int(response[0]), 'description': ResultCode().getNamedValues().getName(response[0]), 'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']), 'referrals': referralsToList(response['referral']), }

