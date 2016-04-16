"""
"""

# Created on 2016.04.16
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

from ... import SEQUENCE_TYPES, MODIFY_ADD


def add_members_to_groups(connection,
                          members_dn,
                          groups_dn,
                          transaction):

    if not isinstance(members_dn, SEQUENCE_TYPES):
        members_dn = [members_dn]

    if not isinstance(groups_dn, SEQUENCE_TYPES):
        groups_dn = [groups_dn]

    transaction_control = None
    error = False

    if transaction:
        result = connection.extend.novell.start_transaction()
        if not connection.strategy.sync:
            _, result = connection.get_response(result)

        transaction_control = result
        # TODO error checking

    if not error:
        for member in members_dn:
            result = connection.modify(member,
                                       {'securityEquals': (MODIFY_ADD, [group for group in groups_dn]),
                                        'groupMembership': (MODIFY_ADD, [group for group in groups_dn])},
                                       controls=[transaction_control] if transaction else None)
            if not connection.strategy.sync:
                _, result = connection.get_response(result)
            else:
                result = connection.result

            if result['description'] != 'success':
                error = True
                break

    if not error:
        for group in groups_dn:
            result = connection.modify(group,
                                       {'member': (MODIFY_ADD, [member for member in members_dn]),
                                        'equivalentToMe': (MODIFY_ADD, [member for member in members_dn])},
                                       controls=[transaction_control] if transaction else None)
            if not connection.strategy.sync:
                _, result = connection.get_response(result)
            else:
                result = connection.result

            if result['description'] != 'success':
                error = True
                break

    if transaction:
        if error:  # aborts transaction in case of error in the modify operations
            result = connection.extend.novell.end_transaction(commit=False, controls=[transaction_control])
        else:
            result = connection.extend.novell.end_transaction(commit=True, controls=[transaction_control])

        if result['description'] != 'success':
            error = True

    return not error  # return True if no error is raised in the LDAP operations
