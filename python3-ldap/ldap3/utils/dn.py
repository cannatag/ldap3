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