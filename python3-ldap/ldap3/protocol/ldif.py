"""
Created on 2013.12.08

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
from base64 import b64encode
from mailbox import linesep
from os import linesep
from ldap3 import LDIF_LINE_LENGTH
"""
LDIF converter RFC 2849 compliant
"""


def safeLDIFString(value):
    if not value:
        return True

    # check SAFE-INIT-CHAR: < 127, not NUL, LF, CR, SPACE, COLON, LESS-THAN
    if ord(value[0]) > 127 or ord(value[0]) in [0, 10, 13, 32, 58, 60]:
        return False

    # check SAFE-CHAR: < 127 not NUL, LF, CR
    if chr(0) in value or chr(10) in value or chr(13) in value:
        return False

    for char in value:
        if ord(char) > 127:
            return False

    # check last char for SPACE
    if ord(value[-1]) == 32:
        return False

    return True


def convertToLDIF(descriptor, value, base64):
    value = str(value)
    if base64 or not safeLDIFString(value):
        line = descriptor + ':: ' + b64encode(value)
    else:
        line = descriptor + ': ' + value

    # check max line lenght and split as per note 2 of RFC 2849
    lines = [' ' + line[i: i + LDIF_LINE_LENGTH] for i in range(LDIF_LINE_LENGTH, len(line), LDIF_LINE_LENGTH)] if  len(line) > LDIF_LINE_LENGTH else []

    return [line[0:LDIF_LINE_LENGTH]] + lines

def searchResponseToLDIF(entries, allBase64):
    lines = []
    for entry in entries:
        if 'dn' in entry:
            lines.extend(convertToLDIF('dn', entry['dn'], allBase64))
            for attr in entry['attributes']:
                for val in entry['attributes'][attr]:
                    lines.extend(convertToLDIF(attr, val, allBase64))
            lines.append('')
        else:
            raise Exception('Unable to convert to LDIF - missing DN')

    if lines:
        lines.insert(0, 'version: 1')

    return linesep.join(lines)

def addRequestToLDIF(entry, allBase64):
    return 'yyy'

def deleteRequestToLDIF(entry, allBase64):
    return 'vvv'

def modifyRequestToLDIF(entry, allBase64):
    return 'zzz'

def modifyDnRequestToLDIF(entry, allBase64):
    return "www"

def toLDIF(operationType, entries, allBase64):
    if operationType == 'searchResponse':
        return searchResponseToLDIF(entries, allBase64)
    elif operationType == 'addRequest':
        return addRequestToLDIF(entries, allBase64)
    elif operationType == 'deleteRequest':
        return deleteRequestToLDIF(entries, allBase64)
    elif operationType == 'modifyRequest':
        return modifyRequestToLDIF(entries, allBase64)
    elif operationType == 'modifyDnRequest':
        return modifyDnRequestToLDIF(entries, allBase64)
