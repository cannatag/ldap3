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

from ldap3.protocol.rfc4511 import DelRequest, LDAPDN, ResultCode
from ldap3.operation.bind import referralsToList

# DelRequest ::= [APPLICATION 10] LDAPDN


def deleteOperation(dn):
    request = DelRequest(LDAPDN(dn))

    return request


def deleteRequestToDict(request):
    return {'entry': str(request)}


def deleteResponseToDict(response):
    return {'result': int(response[0]), 'description': ResultCode().getNamedValues().getName(response[0]), 'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']), 'referrals': referralsToList(response['referral']), }
