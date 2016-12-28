"""
"""

# Created on 2016.08.09
#
# Author: Giovanni Cannata
#
# Copyright 2016 Giovanni Cannata
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

from ... import SEQUENCE_TYPES, STRING_TYPES

# Validators return True if value is valid, False if value is not valid,
# or a value different from True and False that is a valid value to substitute to the input value

def check_type(input_value, value_type):
    if isinstance(input_value, value_type):
        return True

    if isinstance(input_value, SEQUENCE_TYPES):
        for value in input_value:
            if not isinstance(value, value_type):
                return False
        return True

    return False


def always_valid(name, input_value):
    return True


def validate_generic_single_value(name, input_value):
    if not isinstance(input_value, SEQUENCE_TYPES):
        return True
    if len(input_value) == 1:
        return True
    return False


def validate_integer(name, input_value):
    return check_type(input_value, int)


def validate_bytes(name, input_value):
    return check_type(input_value, bytes)


def validate_boolean(name, input_value):
    # it could be a real bool or the string TRUE or FALSE, # only a single valued is allowed
    if validate_generic_single_value(name, input_value):
        if isinstance(input_value, SEQUENCE_TYPES):
            input_value = input_value[0]
        if isinstance(input_value, bool):
            if input_value:
                return 'TRUE'
            else:
                return 'FALSE'
        if isinstance(input_value, STRING_TYPES):
            if input_value.lower() == 'true':
                return 'TRUE'
            elif input_value.lower() == 'false':
                return 'FALSE'

    return False
