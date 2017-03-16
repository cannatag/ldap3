"""
"""

# Created on 2016.08.09
#
# Author: Giovanni Cannata
#
# Copyright 2016, 2017 Giovanni Cannata
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

from datetime import datetime

from ... import SEQUENCE_TYPES, STRING_TYPES
from .formatters import format_time

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


def always_valid(input_value):
    return True


def validate_generic_single_value(input_value):
    if not isinstance(input_value, SEQUENCE_TYPES):
        return True
    if len(input_value) == 1:
        return True
    return False


def validate_integer(input_value):
    if check_type(input_value, int):
        return True
    elif isinstance(input_value, STRING_TYPES):
        # integer represented as string, e.g. from a simple query
        # this also ensures RFC 4517 provision for LDIGIT
        if input_value == str(int(input_value)):
            return True
    elif isinstance(input_value, SEQUENCE_TYPES):
        for value in input_value:
            if not ( isinstance(value, STRING_TYPES) and value == str(int(value)) ):
                return False
        return True
    else:
        return False


def validate_bytes(input_value):
    return check_type(input_value, bytes)


def validate_boolean(input_value):
    # it could be a real bool or the string TRUE or FALSE, # only a single valued is allowed
    if validate_generic_single_value(input_value):
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


def validate_time(input_value):
    # if datetime object doesn't have a timezone it's considered local time and is adjusted to UTC
    changed = False
    sequence = True  # indicates if a sequence must be returned
    if not isinstance(input_value, SEQUENCE_TYPES):
        sequence = False
        input_value = [input_value]

    valid_values = []
    for element in input_value:
        if isinstance(element, STRING_TYPES):  # tries to check if it is already be a Generalized Time
            if isinstance(format_time(element), datetime):  # valid Generalized Time string
                valid_values.append(element)
            else:
                return False
        elif isinstance(element, datetime):
            changed = True
            if element.tzinfo:  # a datetime with a timezone
                valid_values.append(element.strftime('%Y%m%d%H%M%SZ%z'))
            else:  # datetime without timezone, assumed local and adjusted to UTC
                offset = datetime.now() - datetime.utcnow()
                valid_values.append((element - offset).strftime('%Y%m%d%H%M%SZ'))
        else:
            return False

    if changed:
        if sequence:
            return valid_values
        else:
            return valid_values[0]
    else:
        return True
