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
from os import linesep
from ldap3 import LDIF_LINE_LENGTH
"""
LDIF converter RFC 2849 compliant
"""


def safeLDIFString(bytesValue):
    if not bytesValue:
        return True

    # check SAFE-INIT-CHAR: < 127, not NUL, LF, CR, SPACE, COLON, LESS-THAN
    if bytesValue[0] > 127 or bytesValue[0] in [0, 10, 13, 32, 58, 60]:
        return False

    # check SAFE-CHAR: < 127 not NUL, LF, CR
    if 0 in bytesValue or 10 in bytesValue or 13 in bytesValue:
        return False

    # check last char for SPACE
    if bytesValue[-1] == 32:
        return False

    for byte in bytesValue:
        if byte > 127:
            return False

    return True

def convertToLDIF(descriptor, value, base64):
    if isinstance(value, str):
        value = bytes(value, encoding = 'UTF-8')
    if base64 or not safeLDIFString(value):
        encoded = b64encode(value)
        line = descriptor + ':: ' + str(encoded, encoding = 'ascii')
    else:
        line = descriptor + ': ' + str(value, encoding = 'ascii')

    # check max line lenght and split as per note 2 of RFC 2849
    lines = [' ' + line[i: i + LDIF_LINE_LENGTH - 1] for i in range(LDIF_LINE_LENGTH, len(line), LDIF_LINE_LENGTH - 1)] if len(line) > LDIF_LINE_LENGTH else []

    return [line[0:LDIF_LINE_LENGTH]] + lines

def searchResponseToLDIF(entries, allBase64):
    lines = []
    for entry in entries:
        if 'dn' in entry:

            lines.extend(convertToLDIF('dn', entry['dn'], allBase64))
            for attr in entry['rawAttributes']:
                for val in entry['rawAttributes'][attr]:
                    lines.extend(convertToLDIF(attr, val, allBase64))
            lines.append('')
        else:
            raise Exception('Unable to convert to LDIF - missing DN')

    if lines:
        lines.insert(0, 'version: 1')
        lines.append('')
        lines.append('# total number of entries: '+  str(len(entries)))

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
