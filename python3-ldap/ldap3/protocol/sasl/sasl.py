"""
Created on 2013.09.11

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

import stringprep
from unicodedata import ucd_3_2_0 as unicode32
from os import urandom
from binascii import hexlify
from ldap3 import AUTH_SASL, RESULT_AUTH_METHOD_NOT_SUPPORTED, LDAPException
# from ...protocol.rfc4511 import SaslCredentials, AuthenticationChoice


def saslPrep(data):
    """
    implement SASLPrep profile as per RFC4013:
    it defines the "SASLprep" profile of the "stringprep" algorithm [StringPrep].
    The profile is designed for use in Simple Authentication and Security
    Layer ([SASL]) mechanisms, such as [PLAIN], [CRAM-MD5], and
    [DIGEST-MD5].  It may be applicable where simple user names and
    passwords are used.  This profile is not intended for use in
    preparing identity strings that are not simple user names (e.g.,
    email addresses, domain names, distinguished names), or where
    identity or password strings that are not character data, or require
    different handling (e.g., case folding).
    """

    # mapping
    preparedData = ''
    for c in data:
        if stringprep.in_table_c12(c):
            # non-ASCII space characters [StringPrep, C.1.2] that can be mapped to SPACE (U+0020)
            preparedData += ' '
        elif stringprep.in_table_b1(c):
            # the "commonly mapped to nothing" characters [StringPrep, B.1] that can be mapped to nothing.
            pass
        else:
            preparedData += c

    # normalizing
    # This profile specifies using Unicode normalization form KC
    # The repertoire is Unicode 3.2 as per RFC 4013 (2)

    preparedData = unicode32.normalize('NFKC', preparedData)

    if not preparedData:
        raise LDAPException('SASLprep error: unable to normalize string')

    # prohibit
    for c in preparedData:
        if stringprep.in_table_c12(c):
            # Non-ASCII space characters [StringPrep, C.1.2]
            raise LDAPException('SASLprep error: non-ASCII space character present')
        elif stringprep.in_table_c21(c):
            # ASCII control characters [StringPrep, C.2.1]
            raise LDAPException('SASLprep error: ASCII control character present')
        elif stringprep.in_table_c22(c):
            # Non-ASCII control characters [StringPrep, C.2.2]
            raise LDAPException('SASLprep error: non-ASCII control character present')
        elif stringprep.in_table_c3(c):
            # Private Use characters [StringPrep, C.3]
            raise LDAPException('SASLprep error: private character present')
        elif stringprep.in_table_c4(c):
            # Non-character code points [StringPrep, C.4]
            raise LDAPException('SASLprep error: non-character code point present')
        elif stringprep.in_table_c5(c):
            # Surrogate code points [StringPrep, C.5]
            raise LDAPException('SASLprep error: surrogate code point present')
        elif stringprep.in_table_c6(c):
            # Inappropriate for plain text characters [StringPrep, C.6]
            raise LDAPException('SASLprep error: inappropriate for plain text character present')
        elif stringprep.in_table_c7(c):
            # Inappropriate for canonical representation characters [StringPrep, C.7]
            raise LDAPException('SASLprep error: inappropriate for canonical representation character present')
        elif stringprep.in_table_c8(c):
            # Change display properties or deprecated characters [StringPrep, C.8]
            raise LDAPException('SASLprep error: change display property or deprecated character present')
        elif stringprep.in_table_c9(c):
            # Tagging characters [StringPrep, C.9]
            raise LDAPException('SASLprep error: tagging character present')

    # check bidi
    # if a string contains any RandALCat character, the string MUST NOT contain any LCat character.
    flagRAndALCat = False
    flagLCat = False
    for c in preparedData:
        if stringprep.in_table_d1(c):
            flagRAndALCat = True
        elif stringprep.in_table_d2(c):
            flagLCat = True

        if flagRAndALCat and flagLCat:
            raise LDAPException('SASLprep error: string cannot contain (R or AL) and L bidirectional chars')

    # If a string contains any RandALCat character, a RandALCat character MUST be the first character of the string
    # and a RandALCat character MUST be the last character of the string.
    if flagRAndALCat and not stringprep.in_table_d1(preparedData[0]) and not stringprep.in_table_d2(preparedData[-1]):
        raise LDAPException('RandALCat character present, must be first and last character of the string')

    return preparedData


def validateSimplePassword(password):
    """
    validate simple password as per RFC4013 using saslPrep:
    """

    if password == '' or password is None:
        raise LDAPException("simple password can't be empty")

    if not isinstance(password, bytes):  # bytes are returned raw, as per rfc (4.2)
        password = saslPrep(password)

    return password


# def addSaslCredentialsToBindRequest(request, mechanism, credentials):
#     saslCredentials = SaslCredentials()
#     saslCredentials['mechanism'] = mechanism
#     if credentials:
#         saslCredentials['credentials'] = credentials
#     request['authentication'] = AuthenticationChoice().setComponentByName('sasl', saslCredentials)
#
#     return request


def abortSaslNegotiation(connection, controls):
    from ldap3.operation.bind import bindOperation
    request = bindOperation(connection.version, AUTH_SASL, None, None, '', None)
    response = connection.postSendSingleResponse(connection.send('bindRequest', request, controls))
    result = connection.getResponse(response)[0] if isinstance(response, int) else connection.result

    return True if result['result'] == RESULT_AUTH_METHOD_NOT_SUPPORTED else False


def sendSaslNegotiation(connection, controls, payload):
    from ldap3.operation.bind import bindOperation
    request = bindOperation(connection.version, AUTH_SASL, None, None, connection.saslMechanism, payload)
    response = connection.postSendSingleResponse(connection.send('bindRequest', request, controls))
    result = connection.getResponse(response)[0] if isinstance(response, int) else connection.result

    return result

def randomHexString(size):
    return str(hexlify(urandom(size)).decode('ascii'))  # str fix for python 2
