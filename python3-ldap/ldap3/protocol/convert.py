"""
Created on 2013.07.24

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
from datetime import datetime, timedelta, tzinfo
from uuid import UUID
from ..core.exceptions import LDAPControlsError, LDAPAttributeError, LDAPObjectClassError
from .rfc4511 import Controls, Control


# from python standard library docs
class OffsetTzInfo(tzinfo):
    """Fixed offset in minutes east from UTC"""

    def __init__(self, offset, name):
        self.offset = offset
        self.name = name
        self._offset = timedelta(minutes=offset)
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):

        return 'OffsetTzInfo(offset={0.offset!r}, name={0.name!r})'.format(self)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return self.name

    def dst(self, dt):
        return timedelta(0)


def attribute_to_dict(attribute):
    return {'type': str(attribute['type']), 'values': [str(val) for val in attribute['vals']]}


def attributes_to_dict(attributes):
    attributes_dict = dict()
    for attribute in attributes:
        attribute_dict = attribute_to_dict(attribute)
        attributes_dict[attribute_dict['type']] = attribute_dict['values']
    return attributes_dict


def referrals_to_list(referrals):
    return [str(referral) for referral in referrals if referral] if referrals else None


def search_refs_to_list(search_refs):
    return [str(search_ref) for search_ref in search_refs if search_ref] if search_refs else None


def sasl_to_dict(sasl):
    return {'mechanism': str(sasl['mechanism']), 'credentials': str(sasl['credentials'])}


def authentication_choice_to_dict(authentication_choice):
    return {'simple': str(authentication_choice['simple']) if authentication_choice.getName() == 'simple' else None, 'sasl': sasl_to_dict(authentication_choice['sasl']) if authentication_choice.getName() == 'sasl' else None}


def decode_referrals(referrals):
    return [str(referral) for referral in referrals if referral] if referrals else None


def partial_attribute_to_dict(modification):
    return {'type': str(modification['type']), 'value': [str(value) for value in modification['vals']]}


def change_to_dict(change):
    return {'operation': int(change['operation']), 'attribute': partial_attribute_to_dict(change['modification'])}


def changes_to_list(changes):
    return [change_to_dict(change) for change in changes]


def attributes_to_list(attributes):
    return [str(attribute) for attribute in attributes]


def ava_to_dict(ava):
    return {'attribute': str(ava['attributeDesc']), 'value': str(ava['assertionValue'])}


def substring_to_dict(substring):
    return {'initial': substring['initial'] if substring['initial'] else '', 'any': [middle for middle in substring['any']] if substring['any'] else '', 'final': substring['final'] if substring['final'] else ''}


def prepare_changes_for_request(changes):
    prepared = {}
    for change in changes:
        prepared[change['attribute']['type']] = (change['operation'], change['attribute']['value'])
    return prepared


def build_controls_list(controls):
    """
    controls is a list of tuple
    each tuple must have 3 elements: the control OID, the criticality, the value
    criticality must be a boolean
    """
    if not controls:
        return None

    if not isinstance(controls, (list, tuple)):
        raise LDAPControlsError('controls must be a list')

    built_controls = Controls()
    for idx, control in enumerate(controls):
        if len(control) == 3 and isinstance(control[1], bool):
            built_control = Control()
            built_control['controlType'] = control[0]
            built_control['criticality'] = control[1]
            built_control['controlValue'] = control[2]
            built_controls.setComponentByPosition(idx, built_control)
        else:
            raise LDAPControlsError('control must be a tuple of 3 elements: controlType, criticality (boolean) and controlValue')

    return built_controls


def validate_assertion_value(schema, name, value):
    if schema and schema.attribute_types is not None:
        if not name.lower() in schema.attribute_types:
            raise LDAPAttributeError('invalid attribute type in assertion: ' + name)
    if not '\\' in value:
        return value.encode('utf-8')
    validated_value = bytearray()
    pos = 0
    while pos < len(value):
        if value[pos] == '\\':
            byte = value[pos + 1: pos + 3]
            if len(byte) == 2:
                try:
                    validated_value.append(int(value[pos + 1: pos + 3], 16))
                    pos += 3
                    continue
                except ValueError:
                    pass
        validated_value += value[pos].encode('utf-8')
        pos += 1

    return bytes(validated_value)


def validate_attribute_value(schema, name, value):
    if schema:
        if schema.attribute_types is not None and not name.lower() in schema.attribute_types:
            raise LDAPAttributeError('invalid attribute type in attribute')
        if schema.object_classes is not None and name.lower() == 'objectclass':
            if value.lower() not in schema.object_classes:
                raise LDAPObjectClassError('invalid class in ObjectClass attribute: ' + value)

    if isinstance(value, str):
        return validate_assertion_value(None, name, value)  # schema already checked, no need to check again

    return value


def format_unicode(raw_value):
    try:
        if str != bytes:  # python3
            return str(raw_value, 'utf-8', errors='strict')
        else:
            return unicode(raw_value, 'utf-8', errors='strict')
    except TypeError:
        pass

    return raw_value


def format_integer(raw_value):
    try:
        return int(raw_value)
    except TypeError:
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
    except TypeError:
        pass
    return raw_value


def format_uuid_le(raw_value):
    try:
        return str(UUID(bytes_le=raw_value))
    except TypeError:
        pass
    return raw_value


def format_boolean(raw_value):
    if raw_value in [b'TRUE', b'true', b'True']:
        return True
    if raw_value in [b'FALSE', b'false', b'False']:
        return False
    return raw_value


def format_time(raw_value):
    """
    From RFC4517:
    A value of the Generalized Time syntax is a character string
    representing a date and time.  The LDAP-specific encoding of a value
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
    """
    if len(raw_value) < 10 or not all((c in b'0123456789+-,.Z' for c in raw_value)) or (b'Z' in raw_value and not raw_value.endswith(b'Z')):  # first ten characters are mandatory and must be numeric or timezone or fraction
        return raw_value

    if b'.' in raw_value or b',' in raw_value:
        # fraction time TODO
        return raw_value

    # sets position for fixed values

    pos_year = 0
    pos_month = 4
    pos_day = 6
    pos_hour = 8
    pos_minute = 10
    pos_second = 12

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
    if len(time) == 2:  # mmZ fomat
        pos_second = None
    elif len(remain) == 0:  # Z format
        pos_minute = None
        pos_second = None
    elif len(time) == 4:  # mmssZ
        pass
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
            timezone = OffsetTzInfo((timezone_hour * 60 + timezone_minute) * (1 if sep == b'+' else -1), u'UTC' + unicode(sep + offset, encoding='utf-8'))

    try:
        return datetime(year=int(raw_value[pos_year: pos_year + 4]),
                        month=int(raw_value[pos_month: pos_month + 2]),
                        day=int(raw_value[pos_day: pos_day + 2]),
                        hour=int(raw_value[pos_hour: pos_hour + 2]),
                        minute=int(raw_value[pos_minute: pos_minute + 2]) if pos_minute else 0,
                        second=int(raw_value[pos_second: pos_second + 2]) if pos_second else 0,
                        tzinfo=timezone)
    except (TypeError, ValueError):
        return raw_value


def format_attribute_values(schema, name, values, custom_formatter):
    """
    Tries to format following the OIDs info and format_helper specification.
    Search for attribute oid, then attribute name (can be multiple), then attrubte syntax
    Precedence is: 1. attribute name
                   2. attribute oid(from schema)
                   3. attribute names (from oid_info)
                   4. attribute syntax (from schema)
    Custom formatters can be defined in Server object and have precedence over the standard_formatters
    If no formatter is found the raw_value is returned as bytes.
    Attributes defined as SINGLE_VALUE in schema are returned as a single object, otherwise are returned as a list of object
    Formatter functions can return any kind of object
    """
    formatter = None
    if schema and schema.attribute_types is not None and name.lower() in schema.attribute_types:
        attr_type = schema.attribute_types[name.lower()]
    else:
        attr_type = None

    if custom_formatter and isinstance(custom_formatter, dict):  # if custom formatters are defined they have precedence over the standard formatters
        if name.lower() in custom_formatter:  # search for attribute name, as returned by the search operation
            formatter = custom_formatter[name.lower()]

        if not formatter and attr_type and attr_type.oid in custom_formatter:  # search for attribute oid as returned by schema
            formatter = custom_formatter[attr_type.oid]

        if not formatter and attr_type and attr_type.oid_info:
            if isinstance(attr_type.oid_info.name, list):  # search for multiple names defined in oid_info
                for attr_name in attr_type.oid_info.name:
                    if attr_name.lower() in custom_formatter:
                        formatter = custom_formatter[attr_name.lower()]
                        break
            elif attr_type.oid_info.name in custom_formatter:  # search for name defined in oid_info
                formatter = custom_formatter[attr_type.oid_info.name]

        if not formatter and attr_type and attr_type.syntax in custom_formatter:  # search for syntax defined in schema
            formatter = custom_formatter[attr_type.syntax]

    if not formatter and name.lower() in standard_formatter:  # search for attribute name, as returned by the search operation
        formatter = standard_formatter[name.lower()]

    if not formatter and attr_type and attr_type.oid in standard_formatter:  # search for attribute oid as returned by schema
        formatter = standard_formatter[attr_type.oid]

    if not formatter and attr_type and attr_type.oid_info:
        if isinstance(attr_type.oid_info.name, list):  # search for multiple names defined in oid_info
            for attr_name in attr_type.oid_info.name:
                if attr_name.lower() in standard_formatter:
                    formatter = standard_formatter[attr_name.lower()]
                    break
        elif attr_type.oid_info.name in standard_formatter:  # search for name defined in oid_info
            formatter = standard_formatter[attr_type.oid_info.name]

    if not formatter and attr_type and attr_type.syntax in standard_formatter:  # search for syntax defined in schema
        formatter = standard_formatter[attr_type.syntax]

    if not formatter:
        formatter = format_unicode  # default formatter

    formatted_values = [formatter(raw_value) for raw_value in values]
    return formatted_values[0] if (attr_type and attr_type.single_value) else formatted_values


standard_formatter = {
    '1.3.6.1.4.1.1466.115.121.1.1': format_binary,  # ACI item [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.2': format_binary,  # Access point [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.3': format_unicode,  # Attribute type description
    '1.3.6.1.4.1.1466.115.121.1.4': format_binary,  # Audio [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.5': format_binary,  # Binary [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.6': format_unicode,  # Bit String
    '1.3.6.1.4.1.1466.115.121.1.7': format_boolean,  # Boolean
    '1.3.6.1.4.1.1466.115.121.1.8': format_binary,  # Certificate [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.9': format_binary,  # Certificate List [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.10': format_binary,  # Certificate Pair [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.11': format_unicode,  # Country String
    '1.3.6.1.4.1.1466.115.121.1.12': format_unicode,  # Distinguished name (DN)
    '1.3.6.1.4.1.1466.115.121.1.13': format_binary,  # Data Quality Syntax [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.14': format_unicode,  # Delivery method
    '1.3.6.1.4.1.1466.115.121.1.15': format_unicode,  # Directory string
    '1.3.6.1.4.1.1466.115.121.1.16': format_unicode,  # DIT Content Rule Description
    '1.3.6.1.4.1.1466.115.121.1.17': format_unicode,  # DIT Structure Rule Description
    '1.3.6.1.4.1.1466.115.121.1.18': format_binary,  # DL Submit Permission [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.19': format_binary,  # DSA Quality Syntax [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.20': format_binary,  # DSE Type [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.21': format_binary,  # Enhanced Guide
    '1.3.6.1.4.1.1466.115.121.1.22': format_unicode,  # Facsimile Telephone Number
    '1.3.6.1.4.1.1466.115.121.1.23': format_binary,  # Fax
    '1.3.6.1.4.1.1466.115.121.1.24': format_time,  # Generalized time
    '1.3.6.1.4.1.1466.115.121.1.25': format_binary,  # Guide [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.26': format_unicode,  # IA5 string
    '1.3.6.1.4.1.1466.115.121.1.27': format_integer,  # Integer
    '1.3.6.1.4.1.1466.115.121.1.28': format_binary,  # JPEG
    '1.3.6.1.4.1.1466.115.121.1.29': format_binary,  # Master and Shadow Access Points [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.30': format_unicode,  # Matching rule description
    '1.3.6.1.4.1.1466.115.121.1.31': format_unicode,  # Matching rule use description
    '1.3.6.1.4.1.1466.115.121.1.32': format_unicode,  # Mail Preference [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.33': format_unicode,  # MHS OR Address [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.34': format_unicode,  # Name and optional UID
    '1.3.6.1.4.1.1466.115.121.1.35': format_unicode,  # Name form description
    '1.3.6.1.4.1.1466.115.121.1.36': format_unicode,  # Numeric string
    '1.3.6.1.4.1.1466.115.121.1.37': format_unicode,  # Object class description
    '1.3.6.1.4.1.1466.115.121.1.38': format_unicode,  # OID
    '1.3.6.1.4.1.1466.115.121.1.39': format_unicode,  # Other mailbox
    '1.3.6.1.4.1.1466.115.121.1.40': format_binary,  # Octet string
    '1.3.6.1.4.1.1466.115.121.1.41': format_unicode,  # Postal address
    '1.3.6.1.4.1.1466.115.121.1.42': format_binary,  # Protocol Information [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.43': format_binary,  # Presentation Address [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.44': format_unicode,  # Printable string
    '1.3.6.1.4.1.1466.115.121.1.45': format_binary,  # Subtree specification [OBSOLETE
    '1.3.6.1.4.1.1466.115.121.1.46': format_binary,  # Supplier Information [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.47': format_binary,  # Supplier Or Consumer [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.48': format_binary,  # Supplier And Consumer [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.49': format_binary,  # Supported Algorithm [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.50': format_unicode,  # Telephone number
    '1.3.6.1.4.1.1466.115.121.1.51': format_unicode,  # Teletex terminal identifier
    '1.3.6.1.4.1.1466.115.121.1.52': format_unicode,  # Teletex number
    '1.3.6.1.4.1.1466.115.121.1.53': format_time,  # Utc time  (deprecated)
    '1.3.6.1.4.1.1466.115.121.1.54': format_unicode,  # LDAP syntax description
    '1.3.6.1.4.1.1466.115.121.1.55': format_binary,  # Modify rights [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.56': format_binary,  # LDAP Schema Definition [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.57': format_unicode,  # LDAP Schema Description [OBSOLETE]
    '1.3.6.1.4.1.1466.115.121.1.58': format_unicode,  # Substring assertion
    '1.3.6.1.1.16.1': format_uuid,  # UUID
    '2.16.840.1.113719.1.1.4.1.501': format_uuid,  # GUID (Novell)
    '2.16.840.1.113719.1.1.5.1.0': format_binary,  # Unknown (Novell)
    '2.16.840.1.113719.1.1.5.1.6': format_unicode,  # Case Ignore List (Novell)
    '2.16.840.1.113719.1.1.5.1.12': format_binary,  # Tagged Data (Novell)
    '2.16.840.1.113719.1.1.5.1.13': format_binary,  # Octet List (Novell)
    '2.16.840.1.113719.1.1.5.1.14': format_unicode,  # Tagged String (Novell)
    '2.16.840.1.113719.1.1.5.1.15': format_unicode,  # Tagged Name And String (Novell)
    '2.16.840.1.113719.1.1.5.1.16': format_binary,  # NDS Replica Pointer (Novell)
    '2.16.840.1.113719.1.1.5.1.17': format_unicode,  # NDS ACL (Novell)
    '2.16.840.1.113719.1.1.5.1.19': format_time,  # NDS Timestamp (Novell)
    '2.16.840.1.113719.1.1.5.1.22': format_integer,  # Counter (Novell)
    '2.16.840.1.113719.1.1.5.1.23': format_unicode,  # Tagged Name (Novell)
    '2.16.840.1.113719.1.1.5.1.25': format_unicode,  # Typed Name (Novell)
}
