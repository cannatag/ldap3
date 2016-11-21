"""
"""

# Created on 2014.09.08
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016 Giovanni Cannata
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

from string import hexdigits, ascii_letters, digits

from .. import SEQUENCE_TYPES
from ..core.exceptions import LDAPInvalidDnError


STATE_ANY = 0
STATE_ESCAPE = 1
STATE_ESCAPE_HEX = 2


def _add_ava(ava, decompose, remove_space, space_around_equal):
    if not ava:
        return ''

    space = ' ' if space_around_equal else ''
    attr_name, _, value = ava.partition('=')
    if decompose:
        if remove_space:
            component = (attr_name.strip(), value.strip())
        else:
            component = (attr_name, value)
    else:
        if remove_space:
            component = attr_name.strip() + space + '=' + space + value.strip()
        else:
            component = attr_name + space + '=' + space + value

    return component


def to_dn(iterator, decompose=False, remove_space=False, space_around_equal=False, separate_rdn=False):
    """
    Convert an iterator to a list of dn parts
    if decompose=True return a list of tuple (one for each dn component) else return a list of strings
    if remove_space=True removes unneeded spaces
    if space_around_equal=True add spaces around equal in returned strings
    if separate_rdn=True consider multiple RDNs as different component of DN
    """
    dn = []
    component = ''
    escape_sequence = False
    for c in iterator:
        if c == '\\':  # escape sequence
            escape_sequence = True
        elif escape_sequence and c != ' ':
            escape_sequence = False
        elif c == '+' and separate_rdn:
            dn.append(_add_ava(component, decompose, remove_space, space_around_equal))
            component = ''
            continue
        elif c == ',':
            if '=' in component:
                dn.append(_add_ava(component, decompose, remove_space, space_around_equal))
                component = ''
                continue

        component += c

    dn.append(_add_ava(component, decompose, remove_space, space_around_equal))
    return dn


def _find_first_unescaped(dn, char, pos):
    while True:
        pos = dn.find(char, pos)
        if pos == -1:
            break  # no char found
        if pos > 0 and dn[pos - 1] != '\\':  # unescaped char
            break

        pos += 1

    return pos


def _find_last_unescaped(dn, char, start, stop=0):
    while True:
        stop = dn.rfind(char, start, stop)
        if stop == -1:
            break
        if stop >= 0 and dn[stop - 1] != '\\':
            break

        if stop < start:
            stop = -1
            break

    return stop


def get_next_ava(dn):
    comma = _find_first_unescaped(dn, ',', 0)
    plus = _find_first_unescaped(dn, '+', 0)

    if plus > 0 and (plus < comma or comma == -1):
        equal = _find_first_unescaped(dn, '=', plus + 1)
        if equal > plus + 1:
            plus = _find_last_unescaped(dn, '+', plus, equal)
            return dn[:plus], '+'

    if comma > 0:
        equal = _find_first_unescaped(dn, '=', comma + 1)
        if equal > comma + 1:
            comma = _find_last_unescaped(dn, ',', comma, equal)
            return dn[:comma], ','

    return dn, ''


def split_ava(ava, escape=False, strip=True):
    equal = ava.find('=')
    while equal > 0:  # not first character
        if ava[equal - 1] != '\\':  # not an escaped equal so it must be an ava separator
            # attribute_type1 = ava[0:equal].strip() if strip else ava[0:equal]
            if strip:
                attribute_type = ava[0:equal].strip()
                attribute_value = escape_attribute_value(ava[equal + 1:].strip()) if escape else ava[equal + 1:].strip()
            else:
                attribute_type = ava[0:equal]
                attribute_value = escape_attribute_value(ava[equal + 1:]) if escape else ava[equal + 1:]

            return attribute_type, attribute_value
        equal = ava.find('=', equal + 1)

    return '', (ava.strip if strip else ava)  # if no equal found return only value


def validate_attribute_type(attribute_type):
    if not attribute_type:
        raise LDAPInvalidDnError('attribute type not present')

    if attribute_type == '<GUID':  # patch for AD DirSync
        return True

    for c in attribute_type:
        if not (c in ascii_letters or c in digits or c == '-'):  # allowed uppercase and lowercase letters, digits and hyphen as per RFC 4512
            raise LDAPInvalidDnError('character \'' + c + '\' not allowed in attribute type')

    if attribute_type[0] in digits or attribute_type[0] == '-':  # digits and hyphen not allowed as first character
        raise LDAPInvalidDnError('character \'' + attribute_type[0] + '\' not allowed as first character of attribute type')

    return True


def validate_attribute_value(attribute_value):
    if not attribute_value:
        return False

    if attribute_value[0] == '#':  # only hex characters are valid
        for c in attribute_value:
            if 'c' not in hexdigits:  # allowed only hex digits as per RFC 4514
                raise LDAPInvalidDnError('character ' + c + ' not allowed in hex representation of attribute value')
        if len(attribute_value) % 2 == 0:  # string must be # + HEX HEX (an odd number of chars)
            raise LDAPInvalidDnError('hex representation must be in the form of <HEX><HEX> pairs')
    if attribute_value[0] == ' ':  # space cannot be used as first or last character
        raise LDAPInvalidDnError('SPACE not allowed as first character of attribute value')
    if attribute_value[-1] == ' ':
        raise LDAPInvalidDnError('SPACE not allowed as last character of attribute value')

    state = STATE_ANY
    for c in attribute_value:
        if state == STATE_ANY:
            if c == '\\':
                state = STATE_ESCAPE
            elif c in '"#+,;<=>\00':
                raise LDAPInvalidDnError('special characters ' + c + ' must be escaped')
        elif state == STATE_ESCAPE:
            if c in hexdigits:
                state = STATE_ESCAPE_HEX
            elif c in ' "#+,;<=>\\\00':
                state = STATE_ANY
            else:
                raise LDAPInvalidDnError('invalid escaped character ' + c)
        elif state == STATE_ESCAPE_HEX:
            if c in hexdigits:
                state = STATE_ANY
            else:
                raise LDAPInvalidDnError('invalid escaped character ' + c)

    # final state
    if state != STATE_ANY:
        raise LDAPInvalidDnError('invalid final character')

    return True


def escape_attribute_value(attribute_value):
    if not attribute_value:
        return ''

    if attribute_value[0] == '#':  # with leading SHARP only pairs of hex characters are valid
        valid_hex = True
        if len(attribute_value) % 2 == 0:  # string must be # + HEX HEX (an odd number of chars)
            valid_hex = False

        if valid_hex:
            for c in attribute_value:
                if c not in hexdigits:  # allowed only hex digits as per RFC 4514
                    valid_hex = False
                    break

        if valid_hex:
            return attribute_value

    state = STATE_ANY
    escaped = ''
    tmp_buffer = ''
    for c in attribute_value:
        if state == STATE_ANY:
            if c == '\\':
                state = STATE_ESCAPE
            elif c in '"#+,;<=>\00':
                escaped += '\\' + c
            else:
                escaped += c
        elif state == STATE_ESCAPE:
            if c in hexdigits:
                tmp_buffer = c
                state = STATE_ESCAPE_HEX
            elif c in ' "#+,;<=>\\\00':
                escaped += '\\' + c
                state = STATE_ANY
            else:
                escaped += '\\\\' + c
        elif state == STATE_ESCAPE_HEX:
            if c in hexdigits:
                escaped += '\\' + tmp_buffer + c
            else:
                escaped += '\\\\' + tmp_buffer + c
            tmp_buffer = ''
            state = STATE_ANY

    # final state
    if state == STATE_ESCAPE:
        escaped += '\\\\'
    elif state == STATE_ESCAPE_HEX:
        escaped += '\\\\' + tmp_buffer

    if escaped[0] == ' ':  # leading SPACE must be escaped
        escaped = '\\' + escaped

    if escaped[-1] == ' ' and len(escaped) > 1 and escaped[-2] != '\\':  # trailing SPACE must be escaped
        escaped = escaped[:-1] + '\\ '

    return escaped


def parse_dn(dn, escape=False, strip=True):
    rdns = []
    avas = []
    while dn:
        ava, separator = get_next_ava(dn)  # if returned ava doesn't containg any unescaped equal it'a appended to last ava in avas

        dn = dn[len(ava) + 1:]
        if _find_first_unescaped(ava, '=', 0) > 0 or len(avas) == 0:
            avas.append((ava, separator))
        else:
            avas[len(avas) - 1] = (avas[len(avas) - 1][0] + avas[len(avas) - 1][1] + ava, separator)

    for ava, separator in avas:
        attribute_type, attribute_value = split_ava(ava, escape, strip)

        if not validate_attribute_type(attribute_type):
            raise LDAPInvalidDnError('unable to validate attribute type in ' + ava)

        if not validate_attribute_value(attribute_value):
            raise LDAPInvalidDnError('unable to validate attribute value in ' + ava)

        rdns.append((attribute_type, attribute_value, separator))
        dn = dn[len(ava) + 1:]

    if not rdns:
        raise LDAPInvalidDnError('empty dn')

    return rdns


def safe_dn(dn, decompose=False, reverse=False):
    """
    normalize and escape a dn, if dn is a sequence it is joined.
    the reverse parameter change the join direction of the sequence
    """
    if isinstance(dn, SEQUENCE_TYPES):
        components = [rdn for rdn in dn]
        if reverse:
            dn = ','.join(reversed(components))
        else:
            dn = ','.join(components)
    if decompose:
        escaped_dn = []
    else:
        escaped_dn = ''

    # Active Directory allows looking up objects by putting its GUID in a specially-formatted DN
    # (e.g. '<GUID=7b95f0d5-a3ed-486c-919c-077b8c9731f2>')
    if dn.startswith('<GUID=') and dn.endswith('>'):
        escaped_dn = dn
    elif '@' not in dn and '\\' not in dn:  # active directory UPN (User Principal Name) consist of an account, the at sign (@) and a domain, or the domain level logn name domain\username
        for component in parse_dn(dn, escape=True):
            if decompose:
                escaped_dn.append((component[0], component[1], component[2]))
            else:
                escaped_dn += component[0] + '=' + component[1] + component[2]
    elif '@' in dn and len(dn.split('@')) != 2:
        raise LDAPInvalidDnError('Active Directory User Principal Name must consist of name@domain')
    elif '\\' in dn and len(dn.split('\\')) != 2:
        raise LDAPInvalidDnError('Active Directory Domain Level Logon Name must consist of name\\domain')
    else:
        escaped_dn = dn

    return escaped_dn


def safe_rdn(dn, decompose=False):
    """Returns a list of rdn for the dn, usually there is only one rdn, but it can be more than one when the + sign is used"""
    escaped_rdn = []
    one_more = True
    for component in parse_dn(dn, escape=True):
        if component[2] == '+' or one_more:
            if decompose:
                escaped_rdn.append((component[0], component[1]))
            else:
                escaped_rdn.append(component[0] + '=' + component[1])
            if component[2] == '+':
                one_more = True
            else:
                one_more = False
                break

    if one_more:
        raise LDAPInvalidDnError('bad dn ' + str(dn))

    return escaped_rdn
