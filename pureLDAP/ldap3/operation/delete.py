"""
"""

# Created on 2013.05.31
#
# Author: Giovanni Cannata
#
# Copyright 2015 Giovanni Cannata
#
# This file is part of pureLDAP.
#
# pureLDAP is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pureLDAP is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pureLDAP in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from ..protocol.rfc4511 import DelRequest, LDAPDN, ResultCode
from ..operation.bind import referrals_to_list

# DelRequest ::= [APPLICATION 10] LDAPDN


def delete_operation(dn):
    request = DelRequest(LDAPDN(dn))

    return request


def delete_request_to_dict(request):
    return {'entry': str(request)}


def delete_response_to_dict(response):
    return {'result': int(response[0]),
            'description': ResultCode().getNamedValues().getName(response[0]),
            'dn': str(response['matchedDN']),
            'message': str(response['diagnosticMessage']),
            'referrals': referrals_to_list(response['referral'])}
