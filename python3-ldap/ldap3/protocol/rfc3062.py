"""
Created on 2014.04.28

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

from pyasn1.type.univ import OctetString, Sequence
from pyasn1.type.namedtype import NamedTypes, OptionalNamedType

#Modify password extended operation
#passwdModifyOID OBJECT IDENTIFIER ::= 1.3.6.1.4.1.4203.1.11.1
#PasswdModifyRequestValue ::= SEQUENCE {
#    userIdentity [0] OCTET STRING OPTIONAL
#     oldPasswd [1] OCTET STRING OPTIONAL
#     newPasswd [2] OCTET STRING OPTIONAL }
#
# PasswdModifyResponseValue ::= SEQUENCE {
#     genPasswd [0] OCTET STRING OPTIONAL }


class PasswdModifyRequestValue(Sequence):
    """
    PasswdModifyRequestValue ::= SEQUENCE {
        userIdentity [0] OCTET STRING OPTIONAL
        oldPasswd [1] OCTET STRING OPTIONAL
        newPasswd [2] OCTET STRING OPTIONAL }
    """

    componentType = NamedTypes(OptionalNamedType('userIdentity', OctetString()),
                               OptionalNamedType('oldPasswd', OctetString()),
                               OptionalNamedType('newPasswd', OctetString()))


class PasswdModifyResponseValue(Sequence):
    """
    PasswdModifyResponseValue ::= SEQUENCE {
       genPasswd [0] OCTET STRING OPTIONAL }
    """

    componentType = NamedTypes(OptionalNamedType('genPasswd', OctetString()))
