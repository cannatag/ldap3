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


# LDIF converter RFC 2849 compliant

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
    if not value:
        value = ''

    if isinstance(value, str):
        # value = bytes(value, encoding = 'UTF-8') if str is not bytes else bytearray(value, encoding = 'UTF-8')  # in python2 str IS bytes
        value = bytearray(value, encoding = 'UTF-8')

    if base64 or not safeLDIFString(value):
        encoded = b64encode(value)
        if not isinstance(encoded, str):  # in python3 b64encode returns bytes in python2 returns str
            encoded = str(encoded, encoding = 'ASCII')

        line = descriptor + ':: ' + encoded
    else:
        if not isinstance(value, bytearray):  # python3
            value = str(value, encoding = 'ASCII')
        else:  # python2
            value = value.decode(encoding = 'ASCII')

        line = descriptor + ': ' + value

    # check max line lenght and split as per note 2 of RFC 2849
    lines = [' ' + line[i: i + LDIF_LINE_LENGTH - 1] for i in range(LDIF_LINE_LENGTH, len(line), LDIF_LINE_LENGTH - 1)] if len(line) > LDIF_LINE_LENGTH else []

    return [line[0:LDIF_LINE_LENGTH]] + lines


def addControls(controls, allBase64):
    lines = []
    if controls:
        for control in controls:
            line = 'control: ' + control[0]
            line += ' ' + ('true' if control[1] else 'false')
            if control[2]:
                lines.extend(convertToLDIF(line, control[2], allBase64))

    return lines


def addAttributes(attributes, allBase64):
    lines = []
    ocattr = None
    # objectclass first, even if this is not specified in the RFC
    for attr in attributes:
        if attr.lower() == 'objectclass':
            for val in attributes[attr]:
                lines.extend(convertToLDIF(attr, val, allBase64))
            ocattr = attr
            break

    # remaing attributes
    for attr in attributes:
        if attr != ocattr:
            for val in attributes[attr]:
                lines.extend(convertToLDIF(attr, val, allBase64))

    return lines


def searchResponseToLDIF(entries, allBase64):
    lines = []
    for entry in entries:
        if 'dn' in entry:
            lines.extend(convertToLDIF('dn', entry['dn'], allBase64))
            lines.extend(addAttributes(entry['rawAttributes'], allBase64))
        else:
            raise Exception('Unable to convert to LDIF-CONTENT - missing DN')
        lines.append('')

    if lines:
        lines.append('')
        lines.append('# total number of entries: '+  str(len(entries)))

    return lines


def addRequestToLDIF(entry, allBase64):
    lines = []
    if 'entry' in entry:
        lines.extend(convertToLDIF('dn', entry['entry'], allBase64))
        lines.extend(addControls(entry['controls'], allBase64))
        lines.append('changetype: add')
        lines.extend(addAttributes(entry['attributes'], allBase64))
    else:
        raise Exception('Unable to convert to LDIF-CHANGE-ADD - missing DN ')

    return lines


def deleteRequestToLDIF(entry, allBase64):
    lines = []
    if 'entry' in entry:
        lines.extend(convertToLDIF('dn', entry['entry'], allBase64))
        lines.extend(addControls(entry['controls'], allBase64))
        lines.append('changetype: delete')
    else:
        raise Exception('Unable to convert to LDIF-CHANGE-DELETE - missing DN ')

    return lines


def modifyRequestToLDIF(entry, allBase64):
    lines = []
    if 'entry' in entry:
        lines.extend(convertToLDIF('dn', entry['entry'], allBase64))
        lines.extend(addControls(entry['controls'], allBase64))
        lines.append('changetype: modify')
        if 'changes' in entry:
            for change in entry['changes']:
                lines.append(['add', 'delete', 'replace', 'increment'][change['operation']] + ': ' + change['attribute']['type'])
                for value in change['attribute']['value']:
                    lines.extend(convertToLDIF(change['attribute']['type'], value, allBase64))
                lines.append('-')

    return lines


def modifyDnRequestToLDIF(entry, allBase64):
    lines = []
    if 'entry' in entry:
        lines.extend(convertToLDIF('dn', entry['entry'], allBase64))
        lines.extend(addControls(entry['controls'], allBase64))
        lines.append('changetype: modrdn') if 'newSuperior' in entry and entry['newSuperior'] else lines.append('changetype: moddn')
        lines.extend(convertToLDIF('newrdn', entry['newRdn'], allBase64))
        lines.append('deleteoldrdn: ' + ('0' if entry['deleteOldRdn'] else '1'))
        if 'newSuperior' in entry and entry['newSuperior']:
            lines.extend(convertToLDIF('newsuperior', entry['newSuperior'], allBase64))
    else:
        raise Exception('Unable to convert to LDIF-CHANGE-MODDN - missing DN ')

    return lines


def toLDIF(operationType, entries, allBase64):
    if operationType == 'searchResponse':
        lines = searchResponseToLDIF(entries, allBase64)
    elif operationType == 'addRequest':
        lines = addRequestToLDIF(entries, allBase64)
    elif operationType == 'delRequest':
        lines = deleteRequestToLDIF(entries, allBase64)
    elif operationType == 'modifyRequest':
        lines = modifyRequestToLDIF(entries, allBase64)
    elif operationType == 'modDNRequest':
        lines = modifyDnRequestToLDIF(entries, allBase64)
    else:
        lines = []

    if lines:
        lines.insert(0, 'version: 1')
        return linesep.join(lines)
    else:
        return None
