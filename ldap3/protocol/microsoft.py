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
from pyasn1.type.namedtype import NamedTypes, NamedType
from pyasn1.type.tag import Tag, tagClassApplication, tagFormatConstructed
from pyasn1.type.univ import Sequence, OctetString, Integer
from .rfc4511 import ResultCode, LDAPString, Control
from ..utils.asn1 import encoder
from .controls import build_control


class SicilyBindResponse(Sequence):
    # BindResponse ::= [APPLICATION 1] SEQUENCE {
    #     COMPONENTS OF LDAPResult,
    #     serverSaslCreds    [7] OCTET STRING OPTIONAL }
    tagSet = Sequence.tagSet.tagImplicitly(Tag(tagClassApplication, tagFormatConstructed, 1))
    componentType = NamedTypes(NamedType('resultCode', ResultCode()),
                               NamedType('serverCreds', OctetString()),
                               NamedType('errorMessage', LDAPString())
                               )


class DirSyncControlValue(Sequence):
    # realReplControlValue ::= SEQUENCE {
    #    parentsFirst		integer
    #    maxReturnlength	integer
    #    cookie			    OCTET STRING }

    componentType = NamedTypes(NamedType('parentsFirst', Integer()),
                               NamedType('maxReturnLength', Integer()),
                               NamedType('cookie', OctetString())
                               )


class ExtendedDN(Sequence):
    # A flag value 0 specifies that the GUID and SID values be returned in hexadecimal string
    # A flag value of 1 will return the GUID and SID values in standard string format
    componentType = NamedTypes(NamedType('option', Integer())
                               )


def dir_sync_control(criticality=False, parent_first=True, max_length=65535, cookie=None):
    control_value = DirSyncControlValue()
    control_value.setComponentByName('parentFirst', int(parent_first))
    control_value.setComponentByName('maxReturnLength', int(max_length))
    control_value.setComponentByName('cookie', cookie)

    return build_control('1.2.840.113556.1.4.841', criticality, control_value)


def extended_dn_control(criticality=False, hex_format=False):
    control_value = ExtendedDN()
    control_value.setComponentByName('option', Integer(not hex_format))
    return build_control('1.2.840.113556.1.4.529', criticality, control_value)


def show_deleted_control(criticality=False):
    return build_control('1.2.840.113556.1.4.417', criticality, '', False)
