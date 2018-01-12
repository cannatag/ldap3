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
from calendar import timegm
from uuid import UUID

from ... import SEQUENCE_TYPES, STRING_TYPES
from .formatters import format_time, format_ad_timestamp
from ...utils.conv import to_raw, to_unicode

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

    try:  # object couldn't have a __len__ method
        if len(input_value) == 1:
            return True
    except Exception:
        pass

    return False


def validate_minus_one(input_value):
    """Accept -1 only (used by pwdLastSet in AD)
    """
    if not isinstance(input_value, SEQUENCE_TYPES):
        if input_value == -1 or input_value == '-1':
            return True

    try:  # object couldn't have a __len__ method
        if len(input_value) == 1 and input_value == -1 or input_value == '-1':
            return True
    except Exception:
        pass

    return False


def validate_integer(input_value):
    if check_type(input_value, (float, bool)):
        return False

    if str is bytes:  # Python 2, check for long too
        if check_type(input_value, (int, long)):
            return True
    else:  # Python 3, int only
        if check_type(input_value, int):
            return True

    sequence = True  # indicates if a sequence must be returned
    if not isinstance(input_value, SEQUENCE_TYPES):
        sequence = False
        input_value = [input_value]
    else:
        sequence = True  # indicates if a sequence must be returned

    valid_values = []  # builds a list of valid int values
    from decimal import Decimal, InvalidOperation
    for element in input_value:
        try:  # try to convert any type to int, an invalid conversion raise TypeError or ValueError, doublecheck with Decimal type, if both are valid and equal then then int() value is used
            value = to_unicode(element) if isinstance(element, bytes) else element
            decimal_value = Decimal(value)
            int_value = int(value)
            if decimal_value == int_value:
                valid_values.append(int_value)
            else:
                return False
        except (ValueError, TypeError, InvalidOperation):
            return False

    if sequence:
        return valid_values
    else:
        return valid_values[0]


def validate_bytes(input_value):
    return check_type(input_value, bytes)


def validate_boolean(input_value):
    # it could be a real bool or the string TRUE or FALSE, # only a single valued is allowed
    if validate_generic_single_value(input_value):  # valid only if a single value or a sequence with a single element
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
    if not isinstance(input_value, SEQUENCE_TYPES):
        sequence = False
        input_value = [input_value]
    else:
        sequence = True  # indicates if a sequence must be returned

    valid_values = []
    changed = False
    for element in input_value:
        if isinstance(element, STRING_TYPES):  # tries to check if it is already be a Generalized Time
            if isinstance(format_time(to_raw(element)), datetime):  # valid Generalized Time string
                valid_values.append(element)
            else:
                return False
        elif isinstance(element, datetime):
            changed = True
            if element.tzinfo:  # a datetime with a timezone
                valid_values.append(element.strftime('%Y%m%d%H%M%S%z'))
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


def validate_ad_timestamp(input_value):
    """
    Active Directory stores date/time values as the number of 100-nanosecond intervals
    that have elapsed since the 0 hour on January 1, 1601 till the date/time that is being stored.
    The time is always stored in Greenwich Mean Time (GMT) in the Active Directory.
    """
    if not isinstance(input_value, SEQUENCE_TYPES):
        sequence = False
        input_value = [input_value]
    else:
        sequence = True  # indicates if a sequence must be returned

    valid_values = []
    changed = False
    for element in input_value:
        if isinstance(element, STRING_TYPES):  # tries to check if it is already be a AD timestamp
            if isinstance(format_ad_timestamp(to_raw(element)), datetime):  # valid Generalized Time string
                valid_values.append(element)
            else:
                return False
        elif isinstance(element, datetime):
            changed = True
            if element.tzinfo:  # a datetime with a timezone
                valid_values.append(to_raw((timegm((element).utctimetuple()) + 11644473600) * 10000000, encoding='ascii'))
            else:  # datetime without timezone, assumed local and adjusted to UTC
                offset = datetime.now() - datetime.utcnow()
                valid_values.append(to_raw((timegm((element - offset).timetuple()) + 11644473600) * 10000000, encoding='ascii'))
        else:
            return False

    if changed:
        if sequence:
            return valid_values
        else:
            return valid_values[0]
    else:
        return True


def validate_uuid(input_value):
    """
    object guid in uuid format
    """
    if not isinstance(input_value, SEQUENCE_TYPES):
        sequence = False
        input_value = [input_value]
    else:
        sequence = True  # indicates if a sequence must be returned

    valid_values = []
    changed = False
    for element in input_value:
        if isinstance(element, (bytes, bytearray)):  # assumes bytes are valid
            valid_values.append(element)
        elif isinstance(element,  STRING_TYPES):
            try:
                valid_values.append(UUID(element).bytes)
                changed = True
            except ValueError:
                return False
        else:
            return False

    if changed:
        if sequence:
            return valid_values
        else:
            return valid_values[0]
    else:
        return True


def validate_uuid_le(input_value):
    """
    Active Directory stores objectGUID in uuid_le format
    """
    if not isinstance(input_value, SEQUENCE_TYPES):
        sequence = False
        input_value = [input_value]
    else:
        sequence = True  # indicates if a sequence must be returned

    valid_values = []
    changed = False
    for element in input_value:
        if isinstance(element, (bytes, bytearray)):  # assumes bytes are valid
            valid_values.append(element)
        elif isinstance(element,  STRING_TYPES):
            try:
                valid_values.append(UUID(element).bytes_le)
                changed = True
            except ValueError:
                return False
        else:
            return False

    if changed:
        if sequence:
            return valid_values
        else:
            return valid_values[0]
    else:
        return True
