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

from ldap3.protocol.rfc4511 import ModifyRequest, LDAPDN, Changes, Change, Operation, PartialAttribute, AttributeDescription, \
    Vals, ResultCode
from ldap3.operation.bind import referralsToList
from ldap3.protocol.convert import changesToList


# ModifyRequest ::= [APPLICATION 6] SEQUENCE {
#    object          LDAPDN,
#    changes         SEQUENCE OF change SEQUENCE {
#        operation       ENUMERATED {
#            add     (0),
#            delete  (1),
#            replace (2),
#            ...  },
#    modification    PartialAttribute } }



def modifyOperation(dn, changes):
    # changes is a dictionary in the form 'attribute': [(operation, [val1, val2])]
    # operation is 0 (add), 1 (mod), 2 (replace), 3 (increment)
    # increment as per rfc 4525

    changeList = Changes()
    for pos, attribute in enumerate(changes):
        partialAttribute = PartialAttribute()
        partialAttribute['type'] = AttributeDescription(attribute)
        partialAttribute['vals'] = Vals()
        if isinstance(changes[attribute][1], list):
            for index, value in enumerate(changes[attribute][1]):
                partialAttribute['vals'].setComponentByPosition(index, value)
        else:
            partialAttribute['vals'].setComponentByPosition(0, changes[attribute][1])

        change = Change()
        change['operation'] = Operation(changes[attribute][0])
        change['modification'] = partialAttribute

        changeList[pos] = change

    request = ModifyRequest()
    request['object'] = LDAPDN(dn)
    request['changes'] = changeList

    return request


def modifyRequestToDict(request):
    return {
        'entry': str(request['object']),
        'changes': changesToList(request['changes'])
    }


def modifyResponseToDict(response):
    return {
        'result': int(response[0]),
        'description': ResultCode().getNamedValues().getName(response[0]),
        'message': str(response['diagnosticMessage']),
        'dn': str(response['matchedDN']),
        'referrals': referralsToList(response['referral']),
    }
