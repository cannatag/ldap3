"""
"""

# Created on 2014.10.28
#
# Author: Giovanni Cannata
#
# Copyright 2014, 2015, 2016, 2017 Giovanni Cannata
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

from binascii import hexlify
from uuid import UUID
from datetime import datetime, timedelta

from ...core.timezone import OffsetTzInfo


def format_unicode(raw_value):
    try:
        if str != bytes:  # python3
            return str(raw_value, 'utf-8', errors='strict')
        else:
            return unicode(raw_value, 'utf-8', errors='strict')
    except (TypeError, UnicodeDecodeError):
        pass

    return raw_value


def format_integer(raw_value):
    try:
        return int(raw_value)
    except (TypeError, ValueError):
        pass
    return raw_value


def format_binary(raw_value):
    try:
        return bytes(raw_value)
    except TypeError:
        pass
    return raw_value


def format_uuid(raw_value):
    try:
        return str(UUID(bytes=raw_value))
    except (TypeError, ValueError):
        return format_unicode(raw_value)
    except Exception:
        pass

    return raw_value


def format_uuid_le(raw_value):
    try:
        return str(UUID(bytes_le=raw_value))
    except (TypeError, ValueError):
        return format_unicode(raw_value)
    except Exception:
        pass

    return raw_value


def format_boolean(raw_value):
    if raw_value in [b'TRUE', b'true', b'True']:
        return True
    if raw_value in [b'FALSE', b'false', b'False']:
        return False
    return raw_value


def format_ad_timestamp(raw_value):
    """
    Active Directory stores date/time values as the number of 100-nanosecond intervals
    that have elapsed since the 0 hour on January 1, 1601 till the date/time that is being stored.
    The time is always stored in Greenwich Mean Time (GMT) in the Active Directory.
    """
    if raw_value == b'9223372036854775807':  # max value to be stored in a 64 bit signed int
        return datetime.max  # returns datetime.datetime(9999, 12, 31, 23, 59, 59, 999999)
    try:
        timestamp = int(raw_value)
        return datetime.fromtimestamp(timestamp / 10000000.0 - 11644473600, tz=OffsetTzInfo(0, 'UTC'))  # forces true division in python 2
    except (OSError, OverflowError):  # on Windows backwards timestamps are not allowed
        unix_epoch = datetime.fromtimestamp(0, tz=OffsetTzInfo(0, 'UTC'))
        diff_seconds = timedelta(seconds=timestamp/10000000.0 - 11644473600)
        return unix_epoch + diff_seconds
    except Exception:
        return raw_value


def format_time(raw_value):
    """
    """

    '''
    From RFC4517:
    A value of the Generalized Time syntax is a character string
    representing a date and time. The LDAP-specific encoding of a value
    of this syntax is a restriction of the format defined in [ISO8601],
    and is described by the following ABNF:

    GeneralizedTime = century year month day hour
                       [ minute [ second / leap-second ] ]
                       [ fraction ]
                       g-time-zone

    century = 2(%x30-39) ; "00" to "99"
    year    = 2(%x30-39) ; "00" to "99"
    month   =   ( %x30 %x31-39 ) ; "01" (January) to "09"
            / ( %x31 %x30-32 ) ; "10" to "12"
    day     =   ( %x30 %x31-39 )    ; "01" to "09"
            / ( %x31-32 %x30-39 ) ; "10" to "29"
            / ( %x33 %x30-31 )    ; "30" to "31"
    hour    = ( %x30-31 %x30-39 ) / ( %x32 %x30-33 ) ; "00" to "23"
    minute  = %x30-35 %x30-39                        ; "00" to "59"
    second      = ( %x30-35 %x30-39 ) ; "00" to "59"
    leap-second = ( %x36 %x30 )       ; "60"
    fraction        = ( DOT / COMMA ) 1*(%x30-39)
    g-time-zone     = %x5A  ; "Z"
                    / g-differential
    g-differential  = ( MINUS / PLUS ) hour [ minute ]
        MINUS           = %x2D  ; minus sign ("-")
    '''
    if len(raw_value) < 10 or not all((c in b'0123456789+-,.Z' for c in raw_value)) or (b'Z' in raw_value and not raw_value.endswith(b'Z')):  # first ten characters are mandatory and must be numeric or timezone or fraction
        return raw_value

    # sets position for fixed values

    year = int(raw_value[0: 4])
    month = int(raw_value[4: 6])
    day = int(raw_value[6: 8])
    hour = int(raw_value[8: 10])
    minute = 0
    second = 0
    microsecond = 0

    remain = raw_value[10:]
    if remain and remain.endswith(b'Z'):  # uppercase 'Z'
        sep = b'Z'
    elif b'+' in remain:  # timezone can be specified with +hh[mm] or -hh[mm]
        sep = b'+'
    elif b'-' in remain:
        sep = b'-'
    else:  # timezone not specified
        return raw_value

    time, _, offset = remain.partition(sep)

    if time and (b'.' in time or b',' in time):
        # fraction time
        if time[0] in b',.':
            minute = 6 * int(time[1] if str == bytes else chr(time[1]))
        elif time[2] in b',.':
            minute = int(raw_value[10: 12])
            second = 6 * int(time[3] if str == bytes else chr(time[3]))
        elif time[4] in b',.':
            minute = int(raw_value[10: 12])
            second = int(raw_value[12: 14])
            microsecond = 100000 * int(time[5] if str == bytes else chr(time[5]))
    elif len(time) == 2:  # mmZ format
        minute = int(raw_value[10: 12])
    elif len(remain) == 0:  # Z format
        pass
    elif len(time) == 4:  # mmssZ
        minute = int(raw_value[10: 12])
        second = int(raw_value[12: 14])
    else:
        return raw_value

    if sep == b'Z':  # UTC
        timezone = OffsetTzInfo(0, 'UTC')
    else:  # build timezone
        try:
            if len(offset) == 2:
                timezone_hour = int(offset[:2])
                timezone_minute = 0
            elif len(offset) == 4:
                timezone_hour = int(offset[:2])
                timezone_minute = int(offset[2:4])
            else:  # malformed timezone
                raise ValueError
        except ValueError:
            return raw_value
        if str != bytes:  # python3
            timezone = OffsetTzInfo((timezone_hour * 60 + timezone_minute) * (1 if sep == b'+' else -1), 'UTC' + str(sep + offset, encoding='utf-8'))
        else:
            timezone = OffsetTzInfo((timezone_hour * 60 + timezone_minute) * (1 if sep == b'+' else -1), unicode('UTC' + sep + offset, encoding='utf-8'))

    try:
        return datetime(year=year,
                        month=month,
                        day=day,
                        hour=hour,
                        minute=minute,
                        second=second,
                        microsecond=microsecond,
                        tzinfo=timezone)
    except (TypeError, ValueError):
        return raw_value


def format_sid(raw_value):
    """
    """
    '''
    SID= "S-1-" IdentifierAuthority 1*SubAuthority
           IdentifierAuthority= IdentifierAuthorityDec / IdentifierAuthorityHex
              ; If the identifier authority is < 2^32, the
              ; identifier authority is represented as a decimal
              ; number
              ; If the identifier authority is >= 2^32,
              ; the identifier authority is represented in
              ; hexadecimal
            IdentifierAuthorityDec =  1*10DIGIT
              ; IdentifierAuthorityDec, top level authority of a
              ; security identifier is represented as a decimal number
            IdentifierAuthorityHex = "0x" 12HEXDIG
              ; IdentifierAuthorityHex, the top-level authority of a
              ; security identifier is represented as a hexadecimal number
            SubAuthority= "-" 1*10DIGIT
              ; Sub-Authority is always represented as a decimal number
              ; No leading "0" characters are allowed when IdentifierAuthority
              ; or SubAuthority is represented as a decimal number
              ; All hexadecimal digits must be output in string format,
              ; pre-pended by "0x"

    Revision (1 byte): An 8-bit unsigned integer that specifies the revision level of the SID. This value MUST be set to 0x01.
    SubAuthorityCount (1 byte): An 8-bit unsigned integer that specifies the number of elements in the SubAuthority array. The maximum number of elements allowed is 15.
    IdentifierAuthority (6 bytes): A SID_IDENTIFIER_AUTHORITY structure that indicates the authority under which the SID was created. It describes the entity that created the SID. The Identifier Authority value {0,0,0,0,0,5} denotes SIDs created by the NT SID authority.
    SubAuthority (variable): A variable length array of unsigned 32-bit integers that uniquely identifies a principal relative to the IdentifierAuthority. Its length is determined by SubAuthorityCount.
    '''

    if str != bytes:  # python 3
        revision = int(raw_value[0])
        sub_authority_count = int(raw_value[1])
        identifier_authority = int.from_bytes(raw_value[2:8], byteorder='big')
        if identifier_authority >= 4294967296:  # 2 ^ 32
            identifier_authority = hex(identifier_authority)

        sub_authority = ''
        i = 0
        while i < sub_authority_count:
            sub_authority += '-' + str(int.from_bytes(raw_value[8 + (i * 4): 12 + (i * 4)], byteorder='little'))  # little endian
            i += 1
    else:  # python 2
        revision = int(ord(raw_value[0]))
        sub_authority_count = int(ord(raw_value[1]))
        identifier_authority = int(hexlify(raw_value[2:8]), 16)
        if identifier_authority >= 4294967296:  # 2 ^ 32
            identifier_authority = hex(identifier_authority)

        sub_authority = ''
        i = 0
        while i < sub_authority_count:
            sub_authority += '-' + str(int(hexlify(raw_value[11 + (i * 4): 7 + (i * 4): -1]), 16))  # little endian
            i += 1
    return 'S-' + str(revision) + '-' + str(identifier_authority) + sub_authority
