"""
"""

# Created on 2014.09.08
#
# Author: Giovanni Cannata
#
# Copyright 2014 Giovanni Cannata
#
# This file is part of python3-ldap.
#
# python3-ldap is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python3-ldap is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with python3-ldap in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

from ldap3.core.exceptions import LDAPExceptionError


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
    for pos, c in enumerate(iterator):
        if c in '\\':  # escape sequence
            escape_sequence = True
        elif escape_sequence and c not in whitespace:
            escape_sequence = False
        elif c in '+' and separate_rdn:
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


def parse_dn1(dn):
    """
    Parse dn as per rfc4514
    :param dn:
    :return:
    """
    escaping = False
    # comma = False
    # equal = False
    # first_hex = ''
    # component = ''
    # for pos, c in enumerate(dn):
    #     if c == '\\':
    #         escaping = True
    #         continue
    #     elif escaping and c in ' "+,;<=>\\':
    #         escaping = False
    #         component += '\\' + c
    #     elif escaping and c.lower() in '0123456789abcdef':
    #         first_hex = c
    #     elif escaping and first_hex and c.lower() in '0123456789abcdef':
    #         component += first_hex + c
    #     elif escaping and first_hex:
    #         pass

    l = len(dn)
    starting_pos = 0
    pos = -1
    components = []
    a_found = False  # atribute found (before equal)
    v_found = False  # value found (after equal)
    while pos < l:
        starting_pos = pos + 1
        try:
            pos = dn.index('=', starting_pos)  # search for equal sign ('=')
            if pos > 0 and dn[pos - 1] != '\\':  # ignore escaped '='
                a_found = True
                while pos < l:
                    try:
                        pos = dn.index(',', pos)
                        if dn[pos -1] != '\\':  # ignore escaped '.'
                            components.append(dn[starting_pos: pos])
                            break
                    except:
                        pos = l
                        break
        except:
            break

    components.append(dn[starting_pos:])  # if expected sep is not found get last component

    return components


def parse_dn2(dn):
    token_escaped_comma = None
    token_escaped_equal = None
    token_escaped_plus = None

    for x in range(1, 255):
        if chr(x) not in dn:
            token_escaped_equal = chr(x)
            break

    for x in range(ord(token_escaped_equal) + 1, 255):
        if chr(x) not in dn:
            token_escaped_comma = chr(x)
            break

    for x in range(ord(token_escaped_comma) + 1, 255):
        if chr(x) not in dn:
            token_escaped_plus = chr(x)
            break


    if not (token_escaped_equal and token_escaped_comma and token_escaped_plus):
        raise LDAPExceptionError('unable to parse dn')

    dn = dn.replace('\\=', token_escaped_equal)
    dn = dn.replace('\\,', token_escaped_comma)
    dn = dn.replace('\\+', token_escaped_plus)

    components = dn.split(',')
    rdns = []
    fragment = ''

    for component in reversed(components):
        if fragment:
            rdn = component + '\\,' + fragment
            fragment = ''
        else:
            rdn = component

        if rdn == '':
            rdn = '\\,'

        if rdn.count('=') == 1:
            rdns.append(rdn)
        elif rdn.count('=') > 1:
            rdn = rdn.replace('=', '\\=')
            rdn = rdn.replace('\\=', '=', 1)
            rdns.append(rdn)
        else:
            fragment = rdn + fragment

    if fragment:
        rdns.append(fragment)

    avas = []
    for rdn in reversed(rdns):
        ' "+,;<=>\\'
        if ' ' in rdn:
            rdn = rdn.replace(' ', '\\ ')

        if '"' in rdn:
            rdn = rdn.replace('"', '\\"')

        if ';' in rdn:
            rdn = rdn.replace(';', '\\;')

        if '<' in rdn:
            rdn = rdn.replace('<', '\\<')

        if '>' in rdn:
            rdn = rdn.replace('>', '\\>')

        rdn = rdn.replace(token_escaped_equal, '\\=')
        rdn = rdn.replace(token_escaped_comma, '\\,')
        rdn = rdn.replace(token_escaped_plus, '\\+')
        avas.append(rdn)

    return avas

def parse_dn3(dn):
    escaping = False
    comma = False
    equal = False
    first_hex = None
    component = ''
    searching = '='
    pos = 0
    while pos < len(dn):
        c = dn(pos)
        if c == '\\':  # escape sequence
            escaping = True
            continue
        elif escaping and c in ' "+,;<=>\\': # escape 1 byte sequence
            escaping = False
            component += '\\' + c
            continue
        elif escaping and not first_hex and c.lower() in '0123456789abcdef':  # first byte of 2 byte escape sequence (hex value)
            first_hex = c
            continue
        elif escaping and first_hex and c.lower() in '0123456789abcdef':  # second byte of 2 byte escape sequence (hex value)
            component += first_hex + c
            first_hex = None
            continue
        elif escaping and first_hex:  # backslash alone followed by a hex digit, not an escape sequence, revert pos to previous character
            component += '\\' + first_hex
            pos -= 1
            continue
        starting = pos
        found = dn.find(searching)


def parse_dn(dn):
    def _find_valid_token(s):
        """
        :param s: string to analyze
        :return: an unused char to be used as token locally in the string
        """
        nonlocal i
        while i < 256:
            i += 1
            if chr(i) not in s:
                return chr(i)

        raise LDAPExceptionError('unable to tokenize dn')


    escape_table = {
        '\\ ': 0,
        '\\"': 0,
        '\\+': 0,
        '\\,': 0,
        '\\;': 0,
        '\\<': 0,
        '\\=': 0,
        '\\>': 0,
        '\\\\': 0
    }

    for e in ' ";<>':  # escape safe chars
        if e in dn:
            dn = dn.replace(e, '\\' + e)

    i = 0
    for c in escape_table:  # find a suitable unused char value to tokenize escaped values, unusued escaped chars are 0
        if c in dn:
            escape_table[c] = _find_valid_token(dn)

    for e in escape_table:  # tokenize found escaped chars
        if escape_table[e]:
            dn = dn.replace(e, escape_table[e])

    components = dn.split(',')
    rdns = []
    fragment = ''

    for component in reversed(components):
        if fragment:
            rdn = component + '\\,' + fragment
            fragment = ''
        else:
            rdn = component

        if rdn == '':
            rdn = '\\,'

        if rdn.count('=') == 1:
            if '+' in rdn:
                rdn = rdn.replace('+', '\\+')
            rdns.append(rdn)
        elif rdn.count('=') > 1 and not '+' in rdn:
            rdn = rdn.replace('=', '\\=')
            rdn = rdn.replace('\\=', '=', 1)
            rdns.append(rdn)
        elif rdn.count('=') > 1 and '+' in rdn:
            expecting = '='
            temp_rdn = ''
            for c in rdn[::-1]:
                if c == '=' and expecting == '=':
                    expecting = '+'
                elif c == '+' and expecting == '+':
                    expecting = '='
                elif c == '=' and expecting == '+':
                    if not escape_table['\\=']:  # find a valid token for escaped equal if not already set
                        escape_table['\\='] = _find_valid_token(dn)
                    c = escape_table['\\=']
                elif c == '+' and expecting == '=':
                    if not escape_table['\\+']:  # find a valid token for escaped plus if not already set
                        escape_table['\\+'] = _find_valid_token(dn)
                    c = escape_table['\\+']
                temp_rdn += c
            rdns.append(temp_rdn[::-1])
        else:
            fragment = rdn + fragment

    if fragment:
        rdns.append(fragment)

    avas = []
    for rdn in reversed(rdns):
        # escape unenscaped invalid characters
        for e in escape_table:
            if escape_table[e]:
                rdn = rdn.replace(escape_table[e], e)  # untokenize used tokens
        avas.append(rdn)

    return avas