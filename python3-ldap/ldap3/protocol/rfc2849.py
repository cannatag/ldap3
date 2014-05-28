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

from .. import LDIF_LINE_LENGTH
from ..core.exceptions import LDAPLDIFError

# LDIF converter RFC 2849 compliant


def safe_ldif_string(bytes_value):
    if not bytes_value:
        return True

    # check SAFE-INIT-CHAR: < 127, not NUL, LF, CR, SPACE, COLON, LESS-THAN
    if bytes_value[0] > 127 or bytes_value[0] in [0, 10, 13, 32, 58, 60]:
        return False

    # check SAFE-CHAR: < 127 not NUL, LF, CR
    if 0 in bytes_value or 10 in bytes_value or 13 in bytes_value:
        return False

    # check last char for SPACE
    if bytes_value[-1] == 32:
        return False

    for byte in bytes_value:
        if byte > 127:
            return False

    return True


def convert_to_ldif(descriptor, value, base64):
    if not value:
        value = ''
    line = ''
    if isinstance(value, str):
        value = bytearray(value, encoding='utf-8')

    if base64 or not safe_ldif_string(value):
        try:
            encoded = b64encode(value)
        except TypeError:
            encoded = b64encode(str(value))  # patch for Python 2.6
        if not isinstance(encoded, str):  # in Python 3 b64encode returns bytes in Python 2 returns str
            encoded = str(encoded, encoding='ascii')  # Python 3
        line = descriptor + ':: ' + encoded
    else:
        if not isinstance(value, bytearray):  # Python 3
            value = str(value, encoding='ascii')
        else:  # Python 2
            value = str(value)
        line = descriptor + ': ' + value

    return line


def add_controls(controls, all_base64):
    lines = []
    if controls:
        for control in controls:
            line = 'control: ' + control[0]
            line += ' ' + ('true' if control[1] else 'false')
            if control[2]:
                lines.append(convert_to_ldif(line, control[2], all_base64))

    return lines


def add_attributes(attributes, all_base64):
    lines = []
    oc_attr = None
    # objectclass first, even if this is not specified in the RFC
    for attr in attributes:
        if attr.lower() == 'objectclass':
            for val in attributes[attr]:
                lines.append(convert_to_ldif(attr, val, all_base64))
            oc_attr = attr
            break

    # remaining attributes
    for attr in attributes:
        if attr != oc_attr:
            for val in attributes[attr]:
                lines.append(convert_to_ldif(attr, val, all_base64))

    return lines


def search_response_to_ldif(entries, all_base64):
    lines = []
    for entry in entries:
        if 'dn' in entry:
            lines.append(convert_to_ldif('dn', entry['dn'], all_base64))
            lines.extend(add_attributes(entry['raw_attributes'], all_base64))
        else:
            raise LDAPLDIFError('unable to convert to LDIF-CONTENT - missing DN')
        lines.append('')

    if lines:
        lines.append('')
        lines.append('# total number of entries: ' + str(len(entries)))

    return lines


def add_request_to_ldif(entry, all_base64):
    lines = []
    if 'entry' in entry:
        lines.append(convert_to_ldif('dn', entry['entry'], all_base64))
        lines.extend(add_controls(entry['controls'], all_base64))
        lines.append('changetype: add')
        lines.extend(add_attributes(entry['attributes'], all_base64))
    else:
        raise LDAPLDIFError('unable to convert to LDIF-CHANGE-ADD - missing DN ')

    return lines


def delete_request_to_ldif(entry, all_base64):
    lines = []
    if 'entry' in entry:
        lines.append(convert_to_ldif('dn', entry['entry'], all_base64))
        lines.append(add_controls(entry['controls'], all_base64))
        lines.append('changetype: delete')
    else:
        raise LDAPLDIFError('unable to convert to LDIF-CHANGE-DELETE - missing DN ')

    return lines


def modify_request_to_ldif(entry, all_base64):
    lines = []
    if 'entry' in entry:
        lines.append(convert_to_ldif('dn', entry['entry'], all_base64))
        lines.extend(add_controls(entry['controls'], all_base64))
        lines.append('changetype: modify')
        if 'changes' in entry:
            for change in entry['changes']:
                lines.append(['add', 'delete', 'replace', 'increment'][change['operation']] + ': ' + change['attribute']['type'])
                for value in change['attribute']['value']:
                    lines.append(convert_to_ldif(change['attribute']['type'], value, all_base64))
                lines.append('-')

    return lines


def modify_dn_request_to_ldif(entry, all_base64):
    lines = []
    if 'entry' in entry:
        lines.append(convert_to_ldif('dn', entry['entry'], all_base64))
        lines.extend(add_controls(entry['controls'], all_base64))
        lines.append('changetype: modrdn') if 'newSuperior' in entry and entry['newSuperior'] else lines.append('changetype: moddn')
        lines.append(convert_to_ldif('newrdn', entry['newRdn'], all_base64))
        lines.append('deleteoldrdn: ' + ('0' if entry['deleteOldRdn'] else '1'))
        if 'newSuperior' in entry and entry['newSuperior']:
            lines.append(convert_to_ldif('newsuperior', entry['newSuperior'], all_base64))
    else:
        raise LDAPLDIFError('unable to convert to LDIF-CHANGE-MODDN - missing DN ')

    return lines


def operation_to_ldif(operation_type, entries, all_base64=False, sort_order=[]):
    if operation_type == 'searchResponse':
        lines = search_response_to_ldif(entries, all_base64)
    elif operation_type == 'addRequest':
        lines = add_request_to_ldif(entries, all_base64)
    elif operation_type == 'delRequest':
        lines = delete_request_to_ldif(entries, all_base64)
    elif operation_type == 'modifyRequest':
        lines = modify_request_to_ldif(entries, all_base64)
    elif operation_type == 'modDNRequest':
        lines = modify_dn_request_to_ldif(entries, all_base64)
    else:
        lines = []



    # sort lines as per custom sort_order
    # sort order is a list of descriptors, lines will be sorted following the same sequence
    lines = sorted(lines, key=lambda x: x)

    ldif_record = []
    # check max line length and split as per note 2 of RFC 2849
    for line in lines:
        if line:
            ldif_record.append(line[0:LDIF_LINE_LENGTH])
            ldif_record.extend([' ' + line[i: i + LDIF_LINE_LENGTH - 1] for i in range(LDIF_LINE_LENGTH, len(line), LDIF_LINE_LENGTH - 1)] if len(line) > LDIF_LINE_LENGTH else [])

    return ldif_record


def add_ldif_header(ldif_lines):
    if ldif_lines:
        ldif_lines.insert(0, 'version: 1')

    return ldif_lines
