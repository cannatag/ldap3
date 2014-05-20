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

from ..protocol.rfc4511 import ModifyRequest, LDAPDN, Changes, Change, Operation, PartialAttribute, AttributeDescription, Vals, ResultCode
from ..operation.bind import referrals_to_list
from ..protocol.convert import changes_to_list, validate_attribute_value


# ModifyRequest ::= [APPLICATION 6] SEQUENCE {
#    object          LDAPDN,
#    changes         SEQUENCE OF change SEQUENCE {
#        operation       ENUMERATED {
#            add     (0),
#            delete  (1),
#            replace (2),
#            ...  },
#    modification    PartialAttribute } }


def modify_operation(dn,
                     changes,
                     schema=None):
    # changes is a dictionary in the form {'attribute1': [(operation, [val1, val2, ...])], 'attribute2': [(operation, [val1, val2, ...])], ...}
    # operation is 0 (add), 1 (delete), 2 (replace), 3 (increment)
    # increment as per RFC4525

    change_list = Changes()
    for pos, attribute in enumerate(changes):
        partial_attribute = PartialAttribute()
        partial_attribute['type'] = AttributeDescription(attribute)
        partial_attribute['vals'] = Vals()
        if isinstance(changes[attribute][1], list):
            for index, value in enumerate(changes[attribute][1]):
                partial_attribute['vals'].setComponentByPosition(index, validate_attribute_value(schema, attribute, value))
        else:
            partial_attribute['vals'].setComponentByPosition(0, validate_attribute_value(schema, attribute, changes[attribute][1]))

        change = Change()
        change['operation'] = Operation(changes[attribute][0])
        change['modification'] = partial_attribute

        change_list[pos] = change

    request = ModifyRequest()
    request['object'] = LDAPDN(dn)
    request['changes'] = change_list

    return request


def modify_request_to_dict(request):
    return {'entry': str(request['object']), 'changes': changes_to_list(request['changes'])}


def modify_response_to_dict(response):
    return {'result': int(response[0]), 'description': ResultCode().getNamedValues().getName(response[0]), 'message': str(response['diagnosticMessage']), 'dn': str(response['matchedDN']), 'referrals': referrals_to_list(response['referral']), }
