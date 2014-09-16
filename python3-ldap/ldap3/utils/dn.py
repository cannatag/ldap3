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
from string import whitespace
from ..core.exceptions import LDAPExceptionError


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
    for c in escape_table:  # find a suitable unused char value to tokenize escaped values, unused escaped chars are 0
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
        # escape unescaped invalid characters
        for e in escape_table:
            if escape_table[e]:
                rdn = rdn.replace(escape_table[e], e)  # untokenize used tokens
        avas.append(rdn)

    return avas