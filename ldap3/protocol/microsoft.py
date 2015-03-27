"""
"""

# Created on 2015.03.27
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


# SicilyBindResponse ::= [APPLICATION 1] SEQUENCE {
#
#     resultCode   ENUMERATED {
#                      success                     (0),
#                      protocolError               (2),
#                      adminLimitExceeded          (11),
#                      inappropriateAuthentication (48),
#                      invalidCredentials          (49),
#                      busy                        (51),
#                      unavailable                 (52),
#                      unwillingToPerform          (53),
#                      other                       (80) },
#
#     serverCreds  OCTET STRING,
#     errorMessage LDAPString }
from pyasn1.type.namedtype import NamedTypes, NamedType, OptionalNamedType
from pyasn1.type.tag import Tag, tagClassApplication, tagFormatConstructed
from pyasn1.type.univ import Sequence, OctetString
from protocol.rfc4511 import ResultCode, LDAPString


class SicilyBindResponse(Sequence):
    # BindResponse ::= [APPLICATION 1] SEQUENCE {
    #     COMPONENTS OF LDAPResult,
    #     serverSaslCreds    [7] OCTET STRING OPTIONAL }
    tagSet = Sequence.tagSet.tagImplicitly(Tag(tagClassApplication, tagFormatConstructed, 1))
    componentType = NamedTypes(NamedType('resultCode', ResultCode()),
                               NamedType('serverCreds', OctetString()),
                               NamedType('errorMessage', LDAPString())
                               )

